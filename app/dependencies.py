from collections.abc import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.enums import RoleEnum, UserStatusEnum
from app.core.exceptions import (
    InsufficientPermissionsException,
    InvalidTokenException,
    UserNotActiveException,
)
from app.crud import user as user_crud
from app.database import SessionLocal
from app.models.user import User
from app.services.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(token)

    if payload.get("type") == "refresh":
        raise InvalidTokenException()

    login_id = payload.get("sub")
    if not login_id:
        raise InvalidTokenException()

    user = user_crud.get_user_by_user_id(db, login_id)
    if not user:
        raise InvalidTokenException()

    if user.status != UserStatusEnum.active:
        raise UserNotActiveException()

    return user


def require_role(*allowed_roles: RoleEnum):
    """Dependency factory: returns a dependency that ensures the current
    user's role is one of `allowed_roles`."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise InsufficientPermissionsException()
        return current_user

    return role_checker


# Convenience dependencies
get_current_admin = require_role(RoleEnum.admin)
get_current_student = require_role(RoleEnum.student)
