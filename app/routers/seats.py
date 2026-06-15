from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.enums import SeatStatusEnum
from app.crud import seat as seat_crud
from app.dependencies import get_current_admin, get_db
from app.schemas.common import ResponseModel
from app.schemas.seat import PaginatedSeats, SeatCreate, SeatOut, SeatUpdate
from app.services import seat_service

router = APIRouter(
    prefix="/api/v1/admin/seats",
    tags=["Admin - Seat Management"],
    dependencies=[Depends(get_current_admin)],
)


@router.post("", response_model=ResponseModel[SeatOut], status_code=status.HTTP_201_CREATED)
def create_seat(data: SeatCreate, db: Session = Depends(get_db)):
    seat = seat_service.create_seat(db, data)
    return ResponseModel(message="Seat created successfully.", data=SeatOut.model_validate(seat))


@router.get("", response_model=ResponseModel[PaginatedSeats])
def list_seats(
    status_filter: SeatStatusEnum | None = Query(None, alias="status"),
    zone: str | None = None,
    floor: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = seat_crud.list_seats(
        db, status=status_filter, zone=zone, floor=floor, page=page, page_size=page_size
    )
    return ResponseModel(
        data=PaginatedSeats(
            total=total,
            page=page,
            page_size=page_size,
            items=[SeatOut.model_validate(s) for s in items],
        )
    )


@router.get("/{seat_pk}", response_model=ResponseModel[SeatOut])
def get_seat(seat_pk: int, db: Session = Depends(get_db)):
    seat = seat_service.get_seat_or_404(db, seat_pk)
    return ResponseModel(data=SeatOut.model_validate(seat))


@router.patch("/{seat_pk}", response_model=ResponseModel[SeatOut])
def update_seat(seat_pk: int, data: SeatUpdate, db: Session = Depends(get_db)):
    seat = seat_service.update_seat(db, seat_pk, data)
    return ResponseModel(message="Seat updated successfully.", data=SeatOut.model_validate(seat))


@router.delete("/{seat_pk}", response_model=ResponseModel[None])
def delete_seat(seat_pk: int, db: Session = Depends(get_db)):
    seat_service.delete_seat(db, seat_pk)
    return ResponseModel(message="Seat deleted successfully.", data=None)
