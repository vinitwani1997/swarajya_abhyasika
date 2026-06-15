from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import BookingStatusEnum

MAX_DURATION_MONTHS = 12


class BookingCreateSelf(BaseModel):
    """Used by a student to book a seat for themselves."""

    seat_id: int
    start_date: date | None = None  # defaults to today if not provided
    duration_months: int = Field(default=1, ge=1, le=MAX_DURATION_MONTHS)


class BookingCreate(BaseModel):
    """Used by admin to create a booking on behalf of any student."""

    student_id: int
    seat_id: int
    start_date: date | None = None  # defaults to today if not provided
    duration_months: int | None = Field(default=1, ge=1, le=MAX_DURATION_MONTHS)
    end_date: date | None = None  # if provided, overrides duration_months
    notes: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_dates(self) -> "BookingCreate":
        start = self.start_date or date.today()
        if self.end_date is not None and self.end_date <= start:
            raise ValueError("end_date must be after start_date")
        return self


class BookingUpdate(BaseModel):
    """Admin-only full update of a booking."""

    start_date: date | None = None
    end_date: date | None = None
    status: BookingStatusEnum | None = None
    notes: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_dates(self) -> "BookingUpdate":
        if self.start_date is not None and self.end_date is not None:
            if self.end_date <= self.start_date:
                raise ValueError("end_date must be after start_date")
        return self


class StudentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    user_id: str | None


class SeatSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seat_number: str
    zone: str | None
    floor: str | None


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student: StudentSummary
    seat: SeatSummary
    start_date: date
    end_date: date
    status: BookingStatusEnum
    booking_type: str
    created_by: int | None
    cancelled_at: datetime | None
    cancelled_by: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PaginatedBookings(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[BookingOut]
