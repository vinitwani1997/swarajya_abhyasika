from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import NotificationTypeEnum


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: NotificationTypeEnum
    title: str
    message: str
    link: str | None
    is_read: bool
    read_at: datetime | None
    related_entity_type: str | None
    related_entity_id: int | None
    created_at: datetime


class PaginatedNotifications(BaseModel):
    total: int
    page: int
    page_size: int
    unread_count: int
    items: list[NotificationOut]


class NotificationMarkReadRequest(BaseModel):
    """If `notification_ids` is None, all notifications for the current user
    are marked as read."""

    notification_ids: list[int] | None = None


class AdminBroadcastCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    message: str = Field(min_length=1, max_length=500)
    link: str | None = Field(default=None, max_length=255)
    target: Literal["all_students", "all_admins", "specific_user"]
    user_id: int | None = None

    @model_validator(mode="after")
    def validate_user_id(self) -> "AdminBroadcastCreate":
        if self.target == "specific_user" and self.user_id is None:
            raise ValueError("user_id is required when target is 'specific_user'")
        return self
