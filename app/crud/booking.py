from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import BookingStatusEnum
from app.models.booking import Booking


def get_booking_by_id(db: Session, booking_pk: int) -> Booking | None:
    return db.execute(
        select(Booking)
        .options(joinedload(Booking.student), joinedload(Booking.seat))
        .where(Booking.id == booking_pk)
    ).scalar_one_or_none()


def get_active_booking_for_seat(db: Session, seat_id: int) -> Booking | None:
    return db.execute(
        select(Booking).where(
            Booking.seat_id == seat_id, Booking.status == BookingStatusEnum.active
        )
    ).scalar_one_or_none()


def get_active_booking_for_student(db: Session, student_id: int) -> Booking | None:
    return db.execute(
        select(Booking).where(
            Booking.student_id == student_id, Booking.status == BookingStatusEnum.active
        )
    ).scalar_one_or_none()


def create_booking(
    db: Session,
    student_id: int,
    seat_id: int,
    start_date: date,
    end_date: date,
    booking_type: str = "monthly",
    created_by: int | None = None,
    notes: str | None = None,
) -> Booking:
    booking = Booking(
        student_id=student_id,
        seat_id=seat_id,
        start_date=start_date,
        end_date=end_date,
        booking_type=booking_type,
        created_by=created_by,
        notes=notes,
        status=BookingStatusEnum.active,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return get_booking_by_id(db, booking.id)


def update_booking_fields(db: Session, booking: Booking, **fields) -> Booking:
    for key, value in fields.items():
        setattr(booking, key, value)
    db.commit()
    db.refresh(booking)
    return get_booking_by_id(db, booking.id)


def cancel_booking(db: Session, booking: Booking, cancelled_by: int | None) -> Booking:
    booking.status = BookingStatusEnum.cancelled
    booking.cancelled_at = datetime.utcnow()
    booking.cancelled_by = cancelled_by
    db.commit()
    db.refresh(booking)
    return get_booking_by_id(db, booking.id)


def delete_booking(db: Session, booking: Booking) -> None:
    db.delete(booking)
    db.commit()


def list_bookings(
    db: Session,
    student_id: int | None = None,
    seat_id: int | None = None,
    status: BookingStatusEnum | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Booking], int]:
    query = select(Booking).options(joinedload(Booking.student), joinedload(Booking.seat))

    if student_id is not None:
        query = query.where(Booking.student_id == student_id)
    if seat_id is not None:
        query = query.where(Booking.seat_id == seat_id)
    if status is not None:
        query = query.where(Booking.status == status)

    count_query = select(Booking)
    if student_id is not None:
        count_query = count_query.where(Booking.student_id == student_id)
    if seat_id is not None:
        count_query = count_query.where(Booking.seat_id == seat_id)
    if status is not None:
        count_query = count_query.where(Booking.status == status)
    total = len(db.execute(count_query).scalars().all())

    query = (
        query.order_by(Booking.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = db.execute(query).unique().scalars().all()
    return items, total


def expire_overdue_bookings(db: Session) -> list[Booking]:
    """Mark all active bookings whose end_date has passed as expired.
    Returns the list of bookings that were transitioned (with student/seat
    relations loaded, for notification purposes)."""
    today = date.today()
    overdue = db.execute(
        select(Booking)
        .options(joinedload(Booking.student), joinedload(Booking.seat))
        .where(Booking.status == BookingStatusEnum.active, Booking.end_date < today)
    ).unique().scalars().all()

    if overdue:
        for booking in overdue:
            booking.status = BookingStatusEnum.expired
        db.commit()

    return overdue


def get_bookings_ending_in_days(db: Session, days: int) -> list[Booking]:
    """Return active bookings whose end_date is exactly `days` days from today."""
    target_date = date.today() + timedelta(days=days)
    return db.execute(
        select(Booking)
        .options(joinedload(Booking.student), joinedload(Booking.seat))
        .where(Booking.status == BookingStatusEnum.active, Booking.end_date == target_date)
    ).unique().scalars().all()
