from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SeatStatusEnum
from app.database import Base


class Seat(Base):
    __tablename__ = "seats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    seat_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    floor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Monthly price for this seat. If null, the global default
    # (settings.DEFAULT_MONTHLY_SEAT_FEE) is used.
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    status: Mapped[SeatStatusEnum] = mapped_column(
        Enum(SeatStatusEnum, native_enum=False, length=20),
        default=SeatStatusEnum.available,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Seat id={self.id} seat_number={self.seat_number} status={self.status}>"
