from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import PaymentMethodEnum, PaymentStatusEnum
from app.models.payment import Payment


def get_payment_by_id(db: Session, payment_pk: int) -> Payment | None:
    return db.execute(
        select(Payment)
        .options(joinedload(Payment.student), joinedload(Payment.booking))
        .where(Payment.id == payment_pk)
    ).scalar_one_or_none()


def create_payment(
    db: Session,
    student_id: int,
    amount: Decimal,
    due_date: date,
    booking_id: int | None = None,
    currency: str = "INR",
    notes: str | None = None,
) -> Payment:
    payment = Payment(
        student_id=student_id,
        booking_id=booking_id,
        amount=amount,
        currency=currency,
        due_date=due_date,
        notes=notes,
        status=PaymentStatusEnum.pending,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return get_payment_by_id(db, payment.id)


def update_payment_fields(db: Session, payment: Payment, **fields) -> Payment:
    for key, value in fields.items():
        setattr(payment, key, value)
    db.commit()
    db.refresh(payment)
    return get_payment_by_id(db, payment.id)


def mark_paid(
    db: Session,
    payment: Payment,
    method: PaymentMethodEnum,
    recorded_by: int | None,
    transaction_ref: str | None = None,
    notes: str | None = None,
    paid_at: datetime | None = None,
) -> Payment:
    payment.status = PaymentStatusEnum.paid
    payment.method = method
    payment.recorded_by = recorded_by
    payment.transaction_ref = transaction_ref
    payment.paid_at = paid_at or datetime.utcnow()
    if notes:
        payment.notes = notes
    db.commit()
    db.refresh(payment)
    return get_payment_by_id(db, payment.id)


def set_status(
    db: Session, payment: Payment, status: PaymentStatusEnum, notes: str | None = None
) -> Payment:
    payment.status = status
    if notes:
        payment.notes = notes
    db.commit()
    db.refresh(payment)
    return get_payment_by_id(db, payment.id)


def list_payments(
    db: Session,
    student_id: int | None = None,
    status: PaymentStatusEnum | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Payment], int]:
    query = select(Payment).options(joinedload(Payment.student), joinedload(Payment.booking))
    count_query = select(Payment)

    if student_id is not None:
        query = query.where(Payment.student_id == student_id)
        count_query = count_query.where(Payment.student_id == student_id)
    if status is not None:
        query = query.where(Payment.status == status)
        count_query = count_query.where(Payment.status == status)

    total = len(db.execute(count_query).scalars().all())

    query = (
        query.order_by(Payment.due_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = db.execute(query).unique().scalars().all()
    return items, total


def mark_overdue_payments(db: Session) -> list[Payment]:
    """Mark all `pending` payments whose due_date has passed as `overdue`.
    Returns the list of payments that were transitioned (with student
    relation loaded, for notification purposes)."""
    today = date.today()
    overdue = db.execute(
        select(Payment)
        .options(joinedload(Payment.student))
        .where(Payment.status == PaymentStatusEnum.pending, Payment.due_date < today)
    ).unique().scalars().all()

    if overdue:
        for payment in overdue:
            payment.status = PaymentStatusEnum.overdue
        db.commit()

    return overdue


def get_student_dues_summary(db: Session, student_id: int) -> dict:
    due_statuses = (PaymentStatusEnum.pending, PaymentStatusEnum.overdue)

    total_due = db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.student_id == student_id, Payment.status.in_(due_statuses)
        )
    ).scalar_one()

    total_paid = db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.student_id == student_id, Payment.status == PaymentStatusEnum.paid
        )
    ).scalar_one()

    overdue_count = db.execute(
        select(func.count()).where(
            Payment.student_id == student_id, Payment.status == PaymentStatusEnum.overdue
        )
    ).scalar_one()

    pending_count = db.execute(
        select(func.count()).where(
            Payment.student_id == student_id, Payment.status == PaymentStatusEnum.pending
        )
    ).scalar_one()

    return {
        "student_id": student_id,
        "total_due": Decimal(total_due),
        "total_paid": Decimal(total_paid),
        "overdue_count": overdue_count,
        "pending_count": pending_count,
    }


def get_payments_due_in_days(db: Session, days: int) -> list[Payment]:
    """Return pending payments whose due_date is exactly `days` days from today."""
    target_date = date.today() + timedelta(days=days)
    return db.execute(
        select(Payment)
        .options(joinedload(Payment.student))
        .where(Payment.status == PaymentStatusEnum.pending, Payment.due_date == target_date)
    ).unique().scalars().all()
