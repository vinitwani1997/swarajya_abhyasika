from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import RoleEnum, UserStatusEnum
from app.models.user import User
from app.schemas.user import UserAdminCreate, UserRegisterRequest, UserUpdate


def get_user_by_id(db: Session, user_pk: int) -> User | None:
    return db.get(User, user_pk)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def get_user_by_user_id(db: Session, user_id: str) -> User | None:
    return db.execute(select(User).where(User.user_id == user_id)).scalar_one_or_none()


def create_user_from_registration(db: Session, data: UserRegisterRequest) -> User:
    user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        role=RoleEnum.student,
        status=UserStatusEnum.pending,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user_by_admin(db: Session, data: UserAdminCreate) -> User:
    """Admin directly creates a student/user. Account is created pending,
    then immediately approved by the calling service to generate credentials."""
    user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        role=data.role,
        status=UserStatusEnum.pending,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(db: Session, user: User, data: UserUpdate) -> User:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def activate_user_with_credentials(
    db: Session,
    user: User,
    user_id: str,
    hashed_password: str,
    approved_by: int | None = None,
) -> User:
    user.user_id = user_id
    user.hashed_password = hashed_password
    user.status = UserStatusEnum.active
    user.approved_at = datetime.utcnow()
    user.approved_by = approved_by
    db.commit()
    db.refresh(user)
    return user


def reject_user(db: Session, user: User) -> User:
    user.status = UserStatusEnum.rejected
    db.commit()
    db.refresh(user)
    return user


def update_user_status(db: Session, user: User, new_status: UserStatusEnum) -> User:
    user.status = new_status
    db.commit()
    db.refresh(user)
    return user


def list_users(
    db: Session,
    role: RoleEnum | None = None,
    status: UserStatusEnum | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[User], int]:
    query = select(User)
    if role is not None:
        query = query.where(User.role == role)
    if status is not None:
        query = query.where(User.status == status)

    total = len(db.execute(query).scalars().all())

    query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = db.execute(query).scalars().all()
    return items, total


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def get_all_admin_ids(db: Session) -> list[int]:
    """Return IDs of all active admin users (for broadcast notifications)."""
    rows = db.execute(
        select(User.id).where(User.role == RoleEnum.admin, User.status == UserStatusEnum.active)
    ).all()
    return [row[0] for row in rows]


def get_all_active_student_ids(db: Session) -> list[int]:
    """Return IDs of all active student users (for broadcast notifications)."""
    rows = db.execute(
        select(User.id).where(
            User.role == RoleEnum.student, User.status == UserStatusEnum.active
        )
    ).all()
    return [row[0] for row in rows]
