from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.common import ResponseModel
from app.schemas.seat import PaginatedSeats, SeatOut
from app.services import seat_service

router = APIRouter(
    prefix="/api/v1/seats",
    tags=["Seats"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/available", response_model=ResponseModel[PaginatedSeats])
def list_available_seats(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = seat_service.list_available_seats(db, page=page, page_size=page_size)
    return ResponseModel(
        data=PaginatedSeats(
            total=total,
            page=page,
            page_size=page_size,
            items=[SeatOut.model_validate(s) for s in items],
        )
    )
