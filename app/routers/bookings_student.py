from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.booking import BookingCreateSelf, BookingOut, PaginatedBookings
from app.schemas.common import ResponseModel
from app.services import booking_service

router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["Bookings"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=ResponseModel[BookingOut], status_code=status.HTTP_201_CREATED)
def book_seat(
    data: BookingCreateSelf,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = booking_service.book_seat_for_student(db, current_user, data)
    return ResponseModel(
        message="Seat booked successfully. Confirmation email sent.",
        data=BookingOut.model_validate(booking),
    )


@router.get("/me", response_model=ResponseModel[PaginatedBookings])
def get_my_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = booking_service.get_student_bookings(
        db, current_user, page=page, page_size=page_size
    )
    return ResponseModel(
        data=PaginatedBookings(
            total=total,
            page=page,
            page_size=page_size,
            items=[BookingOut.model_validate(b) for b in items],
        )
    )


@router.get("/me/active", response_model=ResponseModel[BookingOut | None])
def get_my_active_booking(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = booking_service.get_student_active_booking(db, current_user)
    return ResponseModel(
        data=BookingOut.model_validate(booking) if booking else None,
        message="No active booking found." if not booking else "OK",
    )


@router.post("/{booking_pk}/cancel", response_model=ResponseModel[BookingOut])
def cancel_my_booking(
    booking_pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = booking_service.cancel_booking(db, booking_pk, current_user=current_user)
    return ResponseModel(
        message="Booking cancelled successfully.", data=BookingOut.model_validate(booking)
    )
