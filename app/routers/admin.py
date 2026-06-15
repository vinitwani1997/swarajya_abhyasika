from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.enums import RoleEnum, UserStatusEnum
from app.core.exceptions import UserNotFoundException
from app.crud import user as user_crud
from app.dependencies import get_current_admin, get_db
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.user import (
    PaginatedUsers,
    UserAdminCreate,
    UserOut,
    UserStatusUpdate,
    UserUpdate,
)
from app.services import auth_service, user_service

router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=["Admin - User Management"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/pending", response_model=ResponseModel[PaginatedUsers])
def list_pending_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = user_crud.list_users(
        db, status=UserStatusEnum.pending, page=page, page_size=page_size
    )
    return ResponseModel(
        data=PaginatedUsers(
            total=total,
            page=page,
            page_size=page_size,
            items=[UserOut.model_validate(u) for u in items],
        )
    )


@router.get("", response_model=ResponseModel[PaginatedUsers])
def list_all_users(
    role: RoleEnum | None = None,
    status_filter: UserStatusEnum | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = user_crud.list_users(
        db, role=role, status=status_filter, page=page, page_size=page_size
    )
    return ResponseModel(
        data=PaginatedUsers(
            total=total,
            page=page,
            page_size=page_size,
            items=[UserOut.model_validate(u) for u in items],
        )
    )


@router.post("", response_model=ResponseModel[UserOut], status_code=status.HTTP_201_CREATED)
def create_user_by_admin(
    data: UserAdminCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = auth_service.admin_create_user(db, data, admin=current_admin)
    return ResponseModel(
        message="User created and activated. Credentials sent via email.",
        data=UserOut.model_validate(user),
    )


@router.post("/{user_pk}/approve", response_model=ResponseModel[UserOut])
def approve_user(
    user_pk: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = auth_service.approve_user(db, user_pk, admin=current_admin)
    return ResponseModel(
        message="User approved and activated. Credentials sent via email.",
        data=UserOut.model_validate(user),
    )


@router.post("/{user_pk}/reject", response_model=ResponseModel[UserOut])
def reject_user(user_pk: int, db: Session = Depends(get_db)):
    user = auth_service.reject_user(db, user_pk)
    return ResponseModel(message="User registration rejected.", data=UserOut.model_validate(user))


@router.get("/{user_pk}", response_model=ResponseModel[UserOut])
def get_user(user_pk: int, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db, user_pk)
    if not user:
        raise UserNotFoundException()
    return ResponseModel(data=UserOut.model_validate(user))


@router.patch("/{user_pk}", response_model=ResponseModel[UserOut])
def update_user(user_pk: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = user_service.update_user_profile(db, user_pk, data)
    return ResponseModel(message="User updated successfully.", data=UserOut.model_validate(user))


@router.patch("/{user_pk}/status", response_model=ResponseModel[UserOut])
def update_user_status(
    user_pk: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = user_service.update_user_status(db, user_pk, data.status, current_admin=current_admin)
    return ResponseModel(
        message=f"User status updated to '{user.status.value}'.",
        data=UserOut.model_validate(user),
    )


@router.delete("/{user_pk}", response_model=ResponseModel[None])
def delete_user(
    user_pk: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user_service.delete_user(db, user_pk, current_admin=current_admin)
    return ResponseModel(message="User deleted successfully.", data=None)
