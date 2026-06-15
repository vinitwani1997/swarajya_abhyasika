from sqlalchemy.orm import Session

from app.core.enums import SeatStatusEnum
from app.core.exceptions import (
    SeatAlreadyExistsException,
    SeatInUseException,
    SeatNotFoundException,
)
from app.crud import booking as booking_crud
from app.crud import seat as seat_crud
from app.models.seat import Seat
from app.schemas.seat import SeatCreate, SeatUpdate


def get_seat_or_404(db: Session, seat_pk: int) -> Seat:
    seat = seat_crud.get_seat_by_id(db, seat_pk)
    if not seat:
        raise SeatNotFoundException()
    return seat


def create_seat(db: Session, data: SeatCreate) -> Seat:
    if seat_crud.get_seat_by_number(db, data.seat_number):
        raise SeatAlreadyExistsException()
    return seat_crud.create_seat(db, data)


def update_seat(db: Session, seat_pk: int, data: SeatUpdate) -> Seat:
    seat = get_seat_or_404(db, seat_pk)

    update_data = data.model_dump(exclude_unset=True)
    new_seat_number = update_data.get("seat_number")
    if new_seat_number and new_seat_number != seat.seat_number:
        existing = seat_crud.get_seat_by_number(db, new_seat_number)
        if existing and existing.id != seat.id:
            raise SeatAlreadyExistsException()

    new_status = update_data.get("status")
    if new_status in (SeatStatusEnum.maintenance, SeatStatusEnum.inactive):
        active_booking = booking_crud.get_active_booking_for_seat(db, seat.id)
        if active_booking:
            raise SeatInUseException(
                detail=(
                    f"Seat has an active booking and cannot be set to "
                    f"'{new_status.value}'. Cancel the booking first."
                )
            )

    return seat_crud.update_seat(db, seat, data)


def delete_seat(db: Session, seat_pk: int) -> None:
    seat = get_seat_or_404(db, seat_pk)

    active_booking = booking_crud.get_active_booking_for_seat(db, seat.id)
    if active_booking:
        raise SeatInUseException(
            detail="Seat has an active booking and cannot be deleted. Cancel the booking first."
        )

    seat_crud.delete_seat(db, seat)


def list_available_seats(db: Session, page: int = 1, page_size: int = 20):
    return seat_crud.list_seats(db, status=SeatStatusEnum.available, page=page, page_size=page_size)
