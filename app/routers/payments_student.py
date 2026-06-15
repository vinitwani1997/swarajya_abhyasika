from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.payment import PaginatedPayments, PaymentOut, StudentDuesSummary
from app.services import payment_service

router = APIRouter(
    prefix="/api/v1/payments",
    tags=["Payments"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/me", response_model=ResponseModel[PaginatedPayments])
def get_my_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = payment_service.get_student_payments(
        db, current_user, page=page, page_size=page_size
    )
    return ResponseModel(
        data=PaginatedPayments(
            total=total,
            page=page,
            page_size=page_size,
            items=[PaymentOut.model_validate(p) for p in items],
        )
    )


@router.get("/me/dues", response_model=ResponseModel[StudentDuesSummary])
def get_my_dues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summary = payment_service.get_student_dues(db, current_user)
    return ResponseModel(data=StudentDuesSummary(**summary))
