from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.enums import BookingStatusEnum
from app.dependencies import get_current_admin, get_db
from app.models.user import User
from app.schemas.booking import (
    BookingCreate,
    BookingOut,
    BookingUpdate,
    PaginatedBookings,
)
from app.schemas.common import ResponseModel
from app.services import booking_service

router = APIRouter(
    prefix="/api/v1/admin/bookings",
    tags=["Admin - Booking Management"],
    dependencies=[Depends(get_current_admin)],
)


@router.post("", response_model=ResponseModel[BookingOut], status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    booking = booking_service.admin_create_booking(db, data, admin=current_admin)
    return ResponseModel(
        message="Booking created successfully. Confirmation email sent.",
        data=BookingOut.model_validate(booking),
    )


@router.get("", response_model=ResponseModel[PaginatedBookings])
def list_bookings(
    student_id: int | None = None,
    seat_id: int | None = None,
    status_filter: BookingStatusEnum | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = booking_service.get_all_bookings(
        db,
        student_id=student_id,
        seat_id=seat_id,
        status=status_filter,
        page=page,
        page_size=page_size,
    )
    return ResponseModel(
        data=PaginatedBookings(
            total=total,
            page=page,
            page_size=page_size,
            items=[BookingOut.model_validate(b) for b in items],
        )
    )


@router.get("/{booking_pk}", response_model=ResponseModel[BookingOut])
def get_booking(booking_pk: int, db: Session = Depends(get_db)):
    booking = booking_service.get_booking_or_404(db, booking_pk)
    return ResponseModel(data=BookingOut.model_validate(booking))


@router.patch("/{booking_pk}", response_model=ResponseModel[BookingOut])
def update_booking(booking_pk: int, data: BookingUpdate, db: Session = Depends(get_db)):
    booking = booking_service.admin_update_booking(db, booking_pk, data)
    return ResponseModel(
        message="Booking updated successfully.", data=BookingOut.model_validate(booking)
    )


@router.post("/{booking_pk}/cancel", response_model=ResponseModel[BookingOut])
def cancel_booking(
    booking_pk: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    booking = booking_service.cancel_booking(db, booking_pk, current_user=current_admin)
    return ResponseModel(
        message="Booking cancelled successfully.", data=BookingOut.model_validate(booking)
    )


@router.delete("/{booking_pk}", response_model=ResponseModel[None])
def delete_booking(booking_pk: int, db: Session = Depends(get_db)):
    booking_service.admin_delete_booking(db, booking_pk)
    return ResponseModel(message="Booking deleted successfully.", data=None)
