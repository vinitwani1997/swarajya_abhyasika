from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import SeatStatusEnum


class SeatCreate(BaseModel):
    seat_number: str = Field(min_length=1, max_length=20)
    floor: str | None = Field(default=None, max_length=50)
    zone: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)

    @field_validator("seat_number")
    @classmethod
    def normalize_seat_number(cls, v: str) -> str:
        return v.strip().upper()


class SeatUpdate(BaseModel):
    seat_number: str | None = Field(default=None, min_length=1, max_length=20)
    floor: str | None = Field(default=None, max_length=50)
    zone: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    status: SeatStatusEnum | None = None

    @field_validator("seat_number")
    @classmethod
    def normalize_seat_number(cls, v: str | None) -> str | None:
        return v.strip().upper() if v else v


class SeatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seat_number: str
    floor: str | None
    zone: str | None
    description: str | None
    price: Decimal | None
    status: SeatStatusEnum
    created_at: datetime
    updated_at: datetime


class PaginatedSeats(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[SeatOut]
