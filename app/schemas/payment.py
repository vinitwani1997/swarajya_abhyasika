from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import PaymentMethodEnum, PaymentStatusEnum
from app.schemas.booking import StudentSummary


class PaymentCreateManual(BaseModel):
    """Admin creates an ad-hoc/manual payment (e.g. penalty, registration fee)."""

    student_id: int
    booking_id: int | None = None
    amount: Decimal = Field(gt=0, decimal_places=2)
    due_date: date
    notes: str | None = Field(default=None, max_length=255)


class PaymentMarkPaid(BaseModel):
    method: PaymentMethodEnum
    transaction_ref: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=255)
    paid_at: datetime | None = None  # defaults to now if not provided


class PaymentUpdate(BaseModel):
    """Admin correction of a payment record (amount, due date, notes)."""

    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    due_date: date | None = None
    notes: str | None = Field(default=None, max_length=255)


class PaymentStatusChange(BaseModel):
    """Used for waive/refund actions. Notes are required for audit trail."""

    notes: str = Field(min_length=1, max_length=255)


class BookingSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_date: date
    end_date: date


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student: StudentSummary
    booking: BookingSummary | None
    amount: Decimal
    currency: str
    status: PaymentStatusEnum
    method: PaymentMethodEnum | None
    due_date: date
    paid_at: datetime | None
    recorded_by: int | None
    transaction_ref: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PaginatedPayments(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[PaymentOut]


class StudentDuesSummary(BaseModel):
    student_id: int
    total_due: Decimal
    total_paid: Decimal
    overdue_count: int
    pending_count: int
