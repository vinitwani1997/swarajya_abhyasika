from datetime import date

from sqlalchemy.orm import Session

from app.core.enums import BookingStatusEnum, RoleEnum, SeatStatusEnum
from app.core.exceptions import (
    BookingAccessDeniedException,
    BookingNotActiveException,
    BookingNotFoundException,
    SeatNotAvailableException,
    SeatNotFoundException,
    StudentAlreadyHasActiveBookingException,
    UserNotFoundException,
)
from app.core.utils import add_months
from app.crud import booking as booking_crud
from app.crud import seat as seat_crud
from app.crud import user as user_crud
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import (
    BookingCreate,
    BookingCreateSelf,
    BookingUpdate,
)
from app.services import notification_service
from app.services.payment_service import create_payment_for_booking


def _expire_overdue_bookings_and_notify(db: Session) -> None:
    expired = booking_crud.expire_overdue_bookings(db)
    notification_service.notify_bookings_expired(db, expired)


def get_booking_or_404(db: Session, booking_pk: int) -> Booking:
    booking = booking_crud.get_booking_by_id(db, booking_pk)
    if not booking:
        raise BookingNotFoundException()
    return booking


def _ensure_seat_bookable(db: Session, seat_id: int) -> None:
    seat = seat_crud.get_seat_by_id(db, seat_id)
    if not seat:
        raise SeatNotFoundException()

    if seat.status in (SeatStatusEnum.maintenance, SeatStatusEnum.inactive):
        raise SeatNotAvailableException(
            detail=f"Seat is currently '{seat.status.value}' and cannot be booked."
        )

    existing_booking = booking_crud.get_active_booking_for_seat(db, seat_id)
    if existing_booking:
        raise SeatNotAvailableException(detail="Seat already has an active booking.")


def _ensure_student_has_no_active_booking(db: Session, student_id: int) -> None:
    existing = booking_crud.get_active_booking_for_student(db, student_id)
    if existing:
        raise StudentAlreadyHasActiveBookingException()


def book_seat_for_student(db: Session, student: User, data: BookingCreateSelf) -> Booking:
    # Lazily expire overdue bookings first so freed seats/slots are reflected.
    _expire_overdue_bookings_and_notify(db)

    _ensure_student_has_no_active_booking(db, student.id)
    _ensure_seat_bookable(db, data.seat_id)

    start = data.start_date or date.today()
    end = add_months(start, data.duration_months)

    booking = booking_crud.create_booking(
        db,
        student_id=student.id,
        seat_id=data.seat_id,
        start_date=start,
        end_date=end,
        booking_type="monthly",
        created_by=None,
    )

    seat = seat_crud.get_seat_by_id(db, data.seat_id)
    seat.status = SeatStatusEnum.occupied
    db.commit()

    create_payment_for_booking(db, booking, seat)

    notification_service.notify_booking_confirmed(
        db, student, seat, booking, created_by_admin=False
    )

    return booking_crud.get_booking_by_id(db, booking.id)


def admin_create_booking(db: Session, data: BookingCreate, admin: User) -> Booking:
    _expire_overdue_bookings_and_notify(db)

    student = user_crud.get_user_by_id(db, data.student_id)
    if not student or student.role != RoleEnum.student:
        raise UserNotFoundException(detail="Student not found")

    _ensure_student_has_no_active_booking(db, student.id)
    _ensure_seat_bookable(db, data.seat_id)

    start = data.start_date or date.today()
    if data.end_date is not None:
        end = data.end_date
    else:
        end = add_months(start, data.duration_months or 1)

    booking = booking_crud.create_booking(
        db,
        student_id=student.id,
        seat_id=data.seat_id,
        start_date=start,
        end_date=end,
        booking_type="monthly",
        created_by=admin.id,
        notes=data.notes,
    )

    seat = seat_crud.get_seat_by_id(db, data.seat_id)
    seat.status = SeatStatusEnum.occupied
    db.commit()

    create_payment_for_booking(db, booking, seat)

    notification_service.notify_booking_confirmed(
        db, student, seat, booking, created_by_admin=True
    )

    return booking_crud.get_booking_by_id(db, booking.id)


def _free_seat_if_unbooked(db: Session, seat_id: int) -> None:
    """Set seat back to available, unless another active booking still claims it."""
    remaining = booking_crud.get_active_booking_for_seat(db, seat_id)
    if remaining:
        return

    seat = seat_crud.get_seat_by_id(db, seat_id)
    if seat and seat.status == SeatStatusEnum.occupied:
        seat.status = SeatStatusEnum.available
        db.commit()


def cancel_booking(db: Session, booking_pk: int, current_user: User) -> Booking:
    booking = get_booking_or_404(db, booking_pk)

    if current_user.role == RoleEnum.student and booking.student_id != current_user.id:
        raise BookingAccessDeniedException()

    if booking.status != BookingStatusEnum.active:
        raise BookingNotActiveException(
            detail=f"Booking is currently '{booking.status.value}' and cannot be cancelled."
        )

    cancelled_by = current_user.id
    booking = booking_crud.cancel_booking(db, booking, cancelled_by=cancelled_by)

    _free_seat_if_unbooked(db, booking.seat_id)

    notification_service.notify_booking_cancelled(
        db, booking, cancelled_by_student=(current_user.role == RoleEnum.student)
    )

    return booking


def admin_update_booking(db: Session, booking_pk: int, data: BookingUpdate) -> Booking:
    booking = get_booking_or_404(db, booking_pk)

    update_data = data.model_dump(exclude_unset=True)
    new_status = update_data.get("status")
    old_status = booking.status

    # Validate resulting date range
    new_start = update_data.get("start_date", booking.start_date)
    new_end = update_data.get("end_date", booking.end_date)
    if new_end <= new_start:
        raise BookingNotActiveException(detail="end_date must be after start_date")

    if new_status == BookingStatusEnum.active and old_status != BookingStatusEnum.active:
        # Re-activating: re-validate seat/student constraints (excluding this booking)
        seat_conflict = booking_crud.get_active_booking_for_seat(db, booking.seat_id)
        if seat_conflict and seat_conflict.id != booking.id:
            raise SeatNotAvailableException(detail="Seat already has another active booking.")

        student_conflict = booking_crud.get_active_booking_for_student(db, booking.student_id)
        if student_conflict and student_conflict.id != booking.id:
            raise StudentAlreadyHasActiveBookingException()

    booking = booking_crud.update_booking_fields(db, booking, **update_data)

    if new_status is not None and new_status != old_status:
        if new_status == BookingStatusEnum.active:
            seat = seat_crud.get_seat_by_id(db, booking.seat_id)
            seat.status = SeatStatusEnum.occupied
            db.commit()
        elif old_status == BookingStatusEnum.active:
            # moved away from active -> free seat if nothing else claims it
            _free_seat_if_unbooked(db, booking.seat_id)

    return booking_crud.get_booking_by_id(db, booking.id)


def admin_delete_booking(db: Session, booking_pk: int) -> None:
    booking = get_booking_or_404(db, booking_pk)

    was_active = booking.status == BookingStatusEnum.active
    seat_id = booking.seat_id

    booking_crud.delete_booking(db, booking)

    if was_active:
        _free_seat_if_unbooked(db, seat_id)


def get_student_bookings(db: Session, student: User, page: int = 1, page_size: int = 20):
    _expire_overdue_bookings_and_notify(db)
    return booking_crud.list_bookings(db, student_id=student.id, page=page, page_size=page_size)


def get_student_active_booking(db: Session, student: User) -> Booking | None:
    _expire_overdue_bookings_and_notify(db)
    return booking_crud.get_active_booking_for_student(db, student.id)


def get_all_bookings(
    db: Session,
    student_id: int | None = None,
    seat_id: int | None = None,
    status: BookingStatusEnum | None = None,
    page: int = 1,
    page_size: int = 20,
):
    _expire_overdue_bookings_and_notify(db)
    return booking_crud.list_bookings(
        db, student_id=student_id, seat_id=seat_id, status=status, page=page, page_size=page_size
    )
