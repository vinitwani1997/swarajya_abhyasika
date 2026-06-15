from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import NotificationNotFoundException
from app.crud import notification as notification_crud
from app.dependencies import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.notification import (
    AdminBroadcastCreate,
    NotificationMarkReadRequest,
    NotificationOut,
    PaginatedNotifications,
)
from app.services import notification_service

router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notifications"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=ResponseModel[PaginatedNotifications])
def list_notifications(
    is_read: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = notification_crud.list_notifications(
        db, user_id=current_user.id, is_read=is_read, page=page, page_size=page_size
    )
    unread_count = notification_crud.get_unread_count(db, current_user.id)

    return ResponseModel(
        data=PaginatedNotifications(
            total=total,
            page=page,
            page_size=page_size,
            unread_count=unread_count,
            items=[NotificationOut.model_validate(n) for n in items],
        )
    )


@router.get("/unread-count", response_model=ResponseModel[int])
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = notification_crud.get_unread_count(db, current_user.id)
    return ResponseModel(data=count)


@router.post("/mark-read", response_model=ResponseModel[None])
def mark_read(
    data: NotificationMarkReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.notification_ids:
        count = notification_crud.mark_many_as_read(db, current_user.id, data.notification_ids)
    else:
        count = notification_crud.mark_all_as_read(db, current_user.id)

    return ResponseModel(message=f"Marked {count} notification(s) as read.", data=None)


@router.post("/{notification_pk}/mark-read", response_model=ResponseModel[NotificationOut])
def mark_single_read(
    notification_pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = notification_crud.get_notification_by_id(db, notification_pk)
    if not notification or notification.user_id != current_user.id:
        raise NotificationNotFoundException()

    notification = notification_crud.mark_as_read(db, notification)
    return ResponseModel(data=NotificationOut.model_validate(notification))


# ---------------------------------------------------------------------------
# Admin broadcast
# ---------------------------------------------------------------------------
admin_router = APIRouter(
    prefix="/api/v1/admin/notifications",
    tags=["Admin - Notifications"],
    dependencies=[Depends(get_current_admin)],
)


@admin_router.post(
    "/broadcast", response_model=ResponseModel[None], status_code=status.HTTP_201_CREATED
)
def broadcast_notification(
    data: AdminBroadcastCreate,
    db: Session = Depends(get_db),
):
    created = notification_service.broadcast(
        db,
        title=data.title,
        message=data.message,
        target=data.target,
        link=data.link,
        user_id=data.user_id,
    )
    return ResponseModel(message=f"Notification sent to {len(created)} user(s).", data=None)
