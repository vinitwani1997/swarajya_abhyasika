from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import RoleEnum, UserStatusEnum


class UserRegisterRequest(BaseModel):
    """Used for student self-registration. Account starts as pending."""

    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)


class UserAdminCreate(BaseModel):
    """Used by admin to directly create a student (auto-activated)."""

    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    role: RoleEnum = RoleEnum.student


class UserUpdate(BaseModel):
    """Partial update of a user's profile."""

    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)


class UserStatusUpdate(BaseModel):
    """Used by admin to manually change a user's status (e.g. activate/deactivate).

    Note: this is NOT for the pending -> approved/rejected workflow, which is
    handled by the dedicated approve/reject endpoints.
    """

    status: UserStatusEnum


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    user_id: str | None
    role: RoleEnum
    status: UserStatusEnum
    is_email_verified: bool
    created_at: datetime
    approved_at: datetime | None


class PaginatedUsers(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[UserOut]
