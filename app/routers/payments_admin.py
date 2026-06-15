from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.enums import PaymentStatusEnum
from app.dependencies import get_current_admin, get_db
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.payment import (
    PaginatedPayments,
    PaymentCreateManual,
    PaymentMarkPaid,
    PaymentOut,
    PaymentStatusChange,
    PaymentUpdate,
    StudentDuesSummary,
)
from app.services import payment_service

router = APIRouter(
    prefix="/api/v1/admin/payments",
    tags=["Admin - Payment Management"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=ResponseModel[PaginatedPayments])
def list_payments(
    student_id: int | None = None,
    status_filter: PaymentStatusEnum | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = payment_service.get_all_payments(
        db, student_id=student_id, status=status_filter, page=page, page_size=page_size
    )
    return ResponseModel(
        data=PaginatedPayments(
            total=total,
            page=page,
            page_size=page_size,
            items=[PaymentOut.model_validate(p) for p in items],
        )
    )


@router.post("", response_model=ResponseModel[PaymentOut], status_code=status.HTTP_201_CREATED)
def create_manual_payment(
    data: PaymentCreateManual,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    payment = payment_service.admin_create_manual_payment(db, data, admin=current_admin)
    return ResponseModel(
        message="Payment record created successfully.", data=PaymentOut.model_validate(payment)
    )


@router.get("/students/{student_pk}/dues", response_model=ResponseModel[StudentDuesSummary])
def get_student_dues(
    student_pk: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    summary = payment_service.get_student_dues_by_id(db, student_pk, current_user=current_admin)
    return ResponseModel(data=StudentDuesSummary(**summary))


@router.get("/{payment_pk}", response_model=ResponseModel[PaymentOut])
def get_payment(payment_pk: int, db: Session = Depends(get_db)):
    payment = payment_service.get_payment_or_404(db, payment_pk)
    return ResponseModel(data=PaymentOut.model_validate(payment))


@router.patch("/{payment_pk}", response_model=ResponseModel[PaymentOut])
def update_payment(payment_pk: int, data: PaymentUpdate, db: Session = Depends(get_db)):
    payment = payment_service.admin_update_payment(db, payment_pk, data)
    return ResponseModel(
        message="Payment updated successfully.", data=PaymentOut.model_validate(payment)
    )


@router.post("/{payment_pk}/mark-paid", response_model=ResponseModel[PaymentOut])
def mark_payment_paid(
    payment_pk: int,
    data: PaymentMarkPaid,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    payment = payment_service.mark_payment_paid(db, payment_pk, data, admin=current_admin)
    return ResponseModel(
        message="Payment marked as paid. Confirmation email sent.",
        data=PaymentOut.model_validate(payment),
    )


@router.post("/{payment_pk}/waive", response_model=ResponseModel[PaymentOut])
def waive_payment(
    payment_pk: int,
    data: PaymentStatusChange,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    payment = payment_service.waive_payment(db, payment_pk, data, admin=current_admin)
    return ResponseModel(
        message="Payment waived successfully.", data=PaymentOut.model_validate(payment)
    )


@router.post("/{payment_pk}/refund", response_model=ResponseModel[PaymentOut])
def refund_payment(
    payment_pk: int,
    data: PaymentStatusChange,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    payment = payment_service.refund_payment(db, payment_pk, data, admin=current_admin)
    return ResponseModel(
        message="Payment marked as refunded.", data=PaymentOut.model_validate(payment)
    )
