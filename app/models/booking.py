from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import BookingStatusEnum
from app.database import Base

if TYPE_CHECKING:
    from app.models.seat import Seat
    from app.models.user import User


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"), nullable=False, index=True)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[BookingStatusEnum] = mapped_column(
        Enum(BookingStatusEnum, native_enum=False, length=20),
        default=BookingStatusEnum.active,
        nullable=False,
        index=True,
    )

    booking_type: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False)

    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    seat: Mapped["Seat"] = relationship("Seat", foreign_keys=[seat_id])
    creator: Mapped["User | None"] = relationship("User", foreign_keys=[created_by])
    canceller: Mapped["User | None"] = relationship("User", foreign_keys=[cancelled_by])

    def __repr__(self) -> str:
        return (
            f"<Booking id={self.id} student_id={self.student_id} "
            f"seat_id={self.seat_id} status={self.status}>"
        )
