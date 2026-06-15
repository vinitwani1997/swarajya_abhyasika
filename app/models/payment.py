from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PaymentMethodEnum, PaymentStatusEnum
from app.database import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    booking_id: Mapped[int | None] = mapped_column(
        ForeignKey("bookings.id"), nullable=True, index=True
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    status: Mapped[PaymentStatusEnum] = mapped_column(
        Enum(PaymentStatusEnum, native_enum=False, length=20),
        default=PaymentStatusEnum.pending,
        nullable=False,
        index=True,
    )
    method: Mapped[PaymentMethodEnum | None] = mapped_column(
        Enum(PaymentMethodEnum, native_enum=False, length=20), nullable=True
    )

    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    transaction_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    booking: Mapped["Booking | None"] = relationship("Booking", foreign_keys=[booking_id])
    recorder: Mapped["User | None"] = relationship("User", foreign_keys=[recorded_by])

    def __repr__(self) -> str:
        return (
            f"<Payment id={self.id} student_id={self.student_id} "
            f"amount={self.amount} status={self.status}>"
        )
