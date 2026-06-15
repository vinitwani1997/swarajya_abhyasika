from sqlalchemy.orm import Session

from app.core.enums import RoleEnum, UserStatusEnum
from app.core.exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    InvalidStatusTransitionException,
    UserNotActiveException,
    UserNotFoundException,
)
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserAdminCreate, UserRegisterRequest
from app.services import security, notification_service


def register_student(db: Session, data: UserRegisterRequest) -> User:
    """Self-registration. Creates a pending student account."""
    if user_crud.get_user_by_email(db, data.email):
        raise EmailAlreadyExistsException()

    user = user_crud.create_user_from_registration(db, data)
    notification_service.notify_registration_submitted(db, user)
    return user


def admin_create_user(db: Session, data: UserAdminCreate, admin: User) -> User:
    """Admin directly creates a user. The account is created and immediately
    activated with generated credentials emailed to the user."""
    if user_crud.get_user_by_email(db, data.email):
        raise EmailAlreadyExistsException()

    user = user_crud.create_user_by_admin(db, data)
    return _activate_and_notify(db, user, approved_by=admin.id)


def approve_user(db: Session, user_pk: int, admin: User) -> User:
    user = user_crud.get_user_by_id(db, user_pk)
    if not user:
        raise UserNotFoundException()

    if user.status != UserStatusEnum.pending:
        raise InvalidStatusTransitionException(
            detail=f"User is currently '{user.status.value}' and cannot be approved."
        )

    return _activate_and_notify(db, user, approved_by=admin.id)


def reject_user(db: Session, user_pk: int) -> User:
    user = user_crud.get_user_by_id(db, user_pk)
    if not user:
        raise UserNotFoundException()

    if user.status != UserStatusEnum.pending:
        raise InvalidStatusTransitionException(
            detail=f"User is currently '{user.status.value}' and cannot be rejected."
        )

    user = user_crud.reject_user(db, user)
    notification_service.notify_account_rejected(db, user)
    return user


def _activate_and_notify(db: Session, user: User, approved_by: int | None) -> User:
    """Generate credentials, activate the user, persist, and notify (in-app + email)."""
    plain_password = security.generate_temp_password()
    hashed_password = security.hash_password(plain_password)
    login_id = security.generate_user_id(user.id)

    user = user_crud.activate_user_with_credentials(
        db,
        user,
        user_id=login_id,
        hashed_password=hashed_password,
        approved_by=approved_by,
    )

    notification_service.notify_account_approved(
        db, user, user_id=login_id, password=plain_password
    )

    return user


def authenticate_user(db: Session, login_id: str, password: str) -> User:
    user = user_crud.get_user_by_user_id(db, login_id)

    if not user or not user.hashed_password:
        raise InvalidCredentialsException()

    if not security.verify_password(password, user.hashed_password):
        raise InvalidCredentialsException()

    if user.status != UserStatusEnum.active:
        raise UserNotActiveException(
            detail=f"Account status is '{user.status.value}'. Please contact admin."
        )

    return user


def create_tokens_for_user(user: User) -> Token:
    token_data = {"sub": user.user_id, "role": user.role.value}
    access_token = security.create_access_token(token_data)
    refresh_token = security.create_refresh_token(token_data)
    return Token(access_token=access_token, refresh_token=refresh_token)


def refresh_access_token(db: Session, refresh_token: str) -> Token:
    payload = security.decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise InvalidCredentialsException(detail="Invalid refresh token")

    login_id = payload.get("sub")
    user = user_crud.get_user_by_user_id(db, login_id) if login_id else None

    if not user or user.status != UserStatusEnum.active:
        raise UserNotActiveException()

    return create_tokens_for_user(user)
