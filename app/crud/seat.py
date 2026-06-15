from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import SeatStatusEnum
from app.models.seat import Seat
from app.schemas.seat import SeatCreate, SeatUpdate


def get_seat_by_id(db: Session, seat_pk: int) -> Seat | None:
    return db.get(Seat, seat_pk)


def get_seat_by_number(db: Session, seat_number: str) -> Seat | None:
    return db.execute(select(Seat).where(Seat.seat_number == seat_number)).scalar_one_or_none()


def create_seat(db: Session, data: SeatCreate) -> Seat:
    seat = Seat(
        seat_number=data.seat_number,
        floor=data.floor,
        zone=data.zone,
        description=data.description,
        price=data.price,
    )
    db.add(seat)
    db.commit()
    db.refresh(seat)
    return seat


def update_seat(db: Session, seat: Seat, data: SeatUpdate) -> Seat:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(seat, field, value)
    db.commit()
    db.refresh(seat)
    return seat


def delete_seat(db: Session, seat: Seat) -> None:
    db.delete(seat)
    db.commit()


def list_seats(
    db: Session,
    status: SeatStatusEnum | None = None,
    zone: str | None = None,
    floor: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Seat], int]:
    query = select(Seat)
    if status is not None:
        query = query.where(Seat.status == status)
    if zone is not None:
        query = query.where(Seat.zone == zone)
    if floor is not None:
        query = query.where(Seat.floor == floor)

    total = len(db.execute(query).scalars().all())

    query = (
        query.order_by(Seat.seat_number.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = db.execute(query).scalars().all()
    return items, total
