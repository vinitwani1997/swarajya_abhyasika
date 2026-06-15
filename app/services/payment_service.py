from datetime import timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import PaymentStatusEnum, RoleEnum
from app.core.exceptions import (
    InvalidPaymentStatusTransitionException,
    PaymentAccessDeniedException,
    PaymentAlreadyPaidException,
    PaymentNotFoundException,
    UserNotFoundException,
)
from app.crud import payment as payment_crud
from app.crud import user as user_crud
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import (
    PaymentCreateManual,
    PaymentMarkPaid,
    PaymentStatusChange,
    PaymentUpdate,
)
from app.services import notification_service


def _mark_overdue_payments_and_notify(db: Session) -> None:
    overdue = payment_crud.mark_overdue_payments(db)
    notification_service.notify_payments_overdue(db, overdue)


def get_payment_or_404(db: Session, payment_pk: int) -> Payment:
    payment = payment_crud.get_payment_by_id(db, payment_pk)
    if not payment:
        raise PaymentNotFoundException()
    return payment


def get_seat_monthly_price(seat) -> Decimal:
    """Return the effective monthly price for a seat, falling back to the
    global default if the seat has no specific price set."""
    if seat.price is not None:
        return Decimal(seat.price)
    return Decimal(str(settings.DEFAULT_MONTHLY_SEAT_FEE))


def create_payment_for_booking(db: Session, booking: Booking, seat) -> Payment:
    """Create a pending payment record for a newly created booking.

    `due_date` = booking.start_date + PAYMENT_DUE_GRACE_DAYS.
    Amount is derived from the seat's price (or global default).
    """
    amount = get_seat_monthly_price(seat)
    due_date = booking.start_date + timedelta(days=settings.PAYMENT_DUE_GRACE_DAYS)

    return payment_crud.create_payment(
        db,
        student_id=booking.student_id,
        amount=amount,
        due_date=due_date,
        booking_id=booking.id,
        currency=settings.PAYMENT_CURRENCY,
    )


def admin_create_manual_payment(db: Session, data: PaymentCreateManual, admin: User) -> Payment:
    student = user_crud.get_user_by_id(db, data.student_id)
    if not student or student.role != RoleEnum.student:
        raise UserNotFoundException(detail="Student not found")

    return payment_crud.create_payment(
        db,
        student_id=data.student_id,
        amount=data.amount,
        due_date=data.due_date,
        booking_id=data.booking_id,
        currency=settings.PAYMENT_CURRENCY,
        notes=data.notes,
    )


def mark_payment_paid(db: Session, payment_pk: int, data: PaymentMarkPaid, admin: User) -> Payment:
    payment = get_payment_or_404(db, payment_pk)

    if payment.status == PaymentStatusEnum.paid:
        raise PaymentAlreadyPaidException()

    if payment.status in (PaymentStatusEnum.waived, PaymentStatusEnum.refunded):
        raise InvalidPaymentStatusTransitionException(
            detail=f"Payment is '{payment.status.value}' and cannot be marked as paid."
        )

    payment = payment_crud.mark_paid(
        db,
        payment,
        method=data.method,
        recorded_by=admin.id,
        transaction_ref=data.transaction_ref,
        notes=data.notes,
        paid_at=data.paid_at,
    )

    notification_service.notify_payment_recorded(db, payment)

    return payment


def admin_update_payment(db: Session, payment_pk: int, data: PaymentUpdate) -> Payment:
    payment = get_payment_or_404(db, payment_pk)

    if payment.status in (PaymentStatusEnum.paid, PaymentStatusEnum.waived, PaymentStatusEnum.refunded):
        raise InvalidPaymentStatusTransitionException(
            detail=f"Payment is '{payment.status.value}' and cannot be edited."
        )

    update_data = data.model_dump(exclude_unset=True)
    return payment_crud.update_payment_fields(db, payment, **update_data)


def waive_payment(db: Session, payment_pk: int, data: PaymentStatusChange, admin: User) -> Payment:
    payment = get_payment_or_404(db, payment_pk)

    if payment.status == PaymentStatusEnum.paid:
        raise InvalidPaymentStatusTransitionException(
            detail="A paid payment cannot be waived. Consider a refund instead."
        )
    if payment.status in (PaymentStatusEnum.waived, PaymentStatusEnum.refunded):
        raise InvalidPaymentStatusTransitionException(
            detail=f"Payment is already '{payment.status.value}'."
        )

    payment = payment_crud.set_status(db, payment, PaymentStatusEnum.waived, notes=data.notes)
    notification_service.notify_payment_waived(db, payment)
    return payment


def refund_payment(db: Session, payment_pk: int, data: PaymentStatusChange, admin: User) -> Payment:
    payment = get_payment_or_404(db, payment_pk)

    if payment.status != PaymentStatusEnum.paid:
        raise InvalidPaymentStatusTransitionException(
            detail="Only a 'paid' payment can be refunded."
        )

    payment = payment_crud.set_status(db, payment, PaymentStatusEnum.refunded, notes=data.notes)
    notification_service.notify_payment_refunded(db, payment)
    return payment


def get_student_payments(db: Session, student: User, page: int = 1, page_size: int = 20):
    _mark_overdue_payments_and_notify(db)
    return payment_crud.list_payments(db, student_id=student.id, page=page, page_size=page_size)


def get_all_payments(
    db: Session,
    student_id: int | None = None,
    status: PaymentStatusEnum | None = None,
    page: int = 1,
    page_size: int = 20,
):
    _mark_overdue_payments_and_notify(db)
    return payment_crud.list_payments(
        db, student_id=student_id, status=status, page=page, page_size=page_size
    )


def get_student_dues(db: Session, student: User):
    _mark_overdue_payments_and_notify(db)
    return payment_crud.get_student_dues_summary(db, student.id)


def get_student_dues_by_id(db: Session, student_pk: int, current_user: User):
    if current_user.role == RoleEnum.student and current_user.id != student_pk:
        raise PaymentAccessDeniedException()

    student = user_crud.get_user_by_id(db, student_pk)
    if not student:
        raise UserNotFoundException(detail="Student not found")

    _mark_overdue_payments_and_notify(db)
    return payment_crud.get_student_dues_summary(db, student.id)
