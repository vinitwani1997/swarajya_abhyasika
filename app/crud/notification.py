from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import NotificationTypeEnum
from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: int,
    type: NotificationTypeEnum,
    title: str,
    message: str,
    link: str | None = None,
    related_entity_type: str | None = None,
    related_entity_id: int | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        link=link,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def bulk_create_notifications(
    db: Session,
    user_ids: list[int],
    type: NotificationTypeEnum,
    title: str,
    message: str,
    link: str | None = None,
    related_entity_type: str | None = None,
    related_entity_id: int | None = None,
) -> list[Notification]:
    notifications = [
        Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            link=link,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )
        for user_id in user_ids
    ]
    db.add_all(notifications)
    db.commit()
    for n in notifications:
        db.refresh(n)
    return notifications


def get_notification_by_id(db: Session, notification_pk: int) -> Notification | None:
    return db.get(Notification, notification_pk)


def list_notifications(
    db: Session,
    user_id: int,
    is_read: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Notification], int]:
    query = select(Notification).where(Notification.user_id == user_id)
    if is_read is not None:
        query = query.where(Notification.is_read == is_read)

    total = len(db.execute(query).scalars().all())

    query = (
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = db.execute(query).scalars().all()
    return items, total


def get_unread_count(db: Session, user_id: int) -> int:
    return db.execute(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
    ).scalar_one()


def mark_as_read(db: Session, notification: Notification) -> Notification:
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user_id: int) -> int:
    notifications = db.execute(
        select(Notification).where(
            Notification.user_id == user_id, Notification.is_read.is_(False)
        )
    ).scalars().all()

    count = len(notifications)
    if count:
        now = datetime.utcnow()
        for n in notifications:
            n.is_read = True
            n.read_at = now
        db.commit()

    return count


def mark_many_as_read(db: Session, user_id: int, notification_ids: list[int]) -> int:
    notifications = db.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.id.in_(notification_ids),
            Notification.is_read.is_(False),
        )
    ).scalars().all()

    count = len(notifications)
    if count:
        now = datetime.utcnow()
        for n in notifications:
            n.is_read = True
            n.read_at = now
        db.commit()

    return count
