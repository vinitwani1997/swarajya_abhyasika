from sqlalchemy.orm import Session

from app.core.enums import RoleEnum, UserStatusEnum
from app.core.exceptions import (
    InvalidOperationException,
    InvalidStatusTransitionException,
    UserNotFoundException,
)
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.user import UserUpdate
from app.services import notification_service


def get_user_or_404(db: Session, user_pk: int) -> User:
    user = user_crud.get_user_by_id(db, user_pk)
    if not user:
        raise UserNotFoundException()
    return user


def update_user_profile(db: Session, user_pk: int, data: UserUpdate) -> User:
    user = get_user_or_404(db, user_pk)
    return user_crud.update_user_profile(db, user, data)


def delete_user(db: Session, user_pk: int, current_admin: User) -> None:
    user = get_user_or_404(db, user_pk)

    if user.id == current_admin.id:
        raise InvalidOperationException(detail="You cannot delete your own account.")

    # NOTE (Phase 3 - Booking): deleting a student who has active bookings
    # will need to either cancel those bookings first or be blocked. Revisit
    # once the booking model exists.
    user_crud.delete_user(db, user)


# Status transitions an admin may apply manually via the status-update endpoint.
# The pending -> active/rejected transitions are intentionally excluded here,
# since those are handled exclusively by the approve/reject endpoints.
_ALLOWED_MANUAL_TRANSITIONS: dict[UserStatusEnum, set[UserStatusEnum]] = {
    UserStatusEnum.active: {UserStatusEnum.inactive},
    UserStatusEnum.inactive: {UserStatusEnum.active},
    UserStatusEnum.rejected: {UserStatusEnum.active},
}


def update_user_status(
    db: Session, user_pk: int, new_status: UserStatusEnum, current_admin: User
) -> User:
    user = get_user_or_404(db, user_pk)

    if user.id == current_admin.id:
        raise InvalidOperationException(detail="You cannot change your own account status.")

    if new_status in (UserStatusEnum.pending, UserStatusEnum.approved):
        raise InvalidStatusTransitionException(
            detail="Use the approve/reject endpoints to manage pending registrations."
        )

    allowed = _ALLOWED_MANUAL_TRANSITIONS.get(user.status, set())
    if new_status not in allowed:
        raise InvalidStatusTransitionException(
            detail=f"Cannot change status from '{user.status.value}' to '{new_status.value}'."
        )

    # Reactivating a rejected/inactive user must not work unless they already
    # have login credentials (i.e. were activated at least once).
    if new_status == UserStatusEnum.active and not user.user_id:
        raise InvalidStatusTransitionException(
            detail="User has never been approved/activated and has no credentials. "
            "Use the approve endpoint instead."
        )

    user = user_crud.update_user_status(db, user, new_status)
    notification_service.notify_account_status_changed(db, user, new_status)
    return user
