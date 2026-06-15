"""Central notification dispatch service.

Every event in the system that should notify a user (in-app and/or via
email) has a corresponding `notify_*` function here. These functions:

1. Create the in-app `Notification` record(s).
2. Send the corresponding email, by calling the existing
   `email_service` functions (email behavior is unchanged from
   Phases 1-4 - this module wraps it, it doesn't replace it).
"""

from app.core.enums import NotificationTypeEnum, UserStatusEnum
from app.crud import notification as notification_crud
from app.crud import user as user_crud
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.seat import Seat
from app.models.user import User
from app.services.email_service import (
    send_booking_confirmation_email,
    send_booking_expiry_reminder_email,
    send_credentials_email,
    send_payment_confirmation_email,
    send_payment_due_reminder_email,
)


# ---------------------------------------------------------------------------
# Account lifecycle
# ---------------------------------------------------------------------------
def notify_registration_submitted(db, student: User) -> None:
    notification_crud.create_notification(
        db,
        user_id=student.id,
        type=NotificationTypeEnum.REGISTRATION_SUBMITTED,
        title="Registration Received",
        message="Your registration is pending admin approval. You'll be notified once approved.",
        related_entity_type="user",
        related_entity_id=student.id,
    )

    admin_ids = user_crud.get_all_admin_ids(db)
    if admin_ids:
        notification_crud.bulk_create_notifications(
            db,
            user_ids=admin_ids,
            type=NotificationTypeEnum.NEW_REGISTRATION,
            title="New Registration",
            message=f"{student.full_name} has registered and is awaiting approval.",
            link=f"/admin/users/{student.id}",
            related_entity_type="user",
            related_entity_id=student.id,
        )


def notify_account_approved(db, student: User, user_id: str, password: str) -> None:
    notification_crud.create_notification(
        db,
        user_id=student.id,
        type=NotificationTypeEnum.ACCOUNT_APPROVED,
        title="Account Approved",
        message="Your account has been approved. Login credentials have been sent to your email.",
        related_entity_type="user",
        related_entity_id=student.id,
    )

    send_credentials_email(
        to_email=student.email,
        full_name=student.full_name,
        user_id=user_id,
        password=password,
    )


def notify_account_rejected(db, student: User) -> None:
    notification_crud.create_notification(
        db,
        user_id=student.id,
        type=NotificationTypeEnum.ACCOUNT_REJECTED,
        title="Registration Rejected",
        message="Your registration request was not approved. Please contact the library for details.",
        related_entity_type="user",
        related_entity_id=student.id,
    )


def notify_account_status_changed(db, student: User, new_status: UserStatusEnum) -> None:
    action = "activated" if new_status == UserStatusEnum.active else "deactivated"
    notification_crud.create_notification(
        db,
        user_id=student.id,
        type=NotificationTypeEnum.ACCOUNT_STATUS_CHANGED,
        title="Account Status Updated",
        message=f"Your account has been {action} by the admin.",
        related_entity_type="user",
        related_entity_id=student.id,
    )


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------
def notify_booking_confirmed(
    db, student: User, seat: Seat, booking: Booking, created_by_admin: bool = False
) -> None:
    notification_crud.create_notification(
        db,
        user_id=student.id,
        type=NotificationTypeEnum.BOOKING_CONFIRMED,
        title="Seat Booked",
        message=(
            f"Seat {seat.seat_number} booked from {booking.start_date.isoformat()} "
            f"to {booking.end_date.isoformat()}."
        ),
        link=f"/bookings/{booking.id}",
        related_entity_type="booking",
        related_entity_id=booking.id,
    )

    send_booking_confirmation_email(
        to_email=student.email,
        full_name=student.full_name,
        seat_number=seat.seat_number,
        start_date=booking.start_date,
        end_date=booking.end_date,
    )

    if not created_by_admin:
        admin_ids = user_crud.get_all_admin_ids(db)
        if admin_ids:
            notification_crud.bulk_create_notifications(
                db,
                user_ids=admin_ids,
                type=NotificationTypeEnum.SEAT_BOOKED,
                title="Seat Booked",
                message=f"{student.full_name} booked seat {seat.seat_number}.",
                link=f"/admin/bookings/{booking.id}",
                related_entity_type="booking",
                related_entity_id=booking.id,
            )


def notify_booking_cancelled(db, booking: Booking, cancelled_by_student: bool) -> None:
    seat_number = booking.seat.seat_number

    notification_crud.create_notification(
        db,
        user_id=booking.student_id,
        type=NotificationTypeEnum.BOOKING_CANCELLED,
        title="Booking Cancelled",
        message=f"Your booking for seat {seat_number} has been cancelled.",
        related_entity_type="booking",
        related_entity_id=booking.id,
    )

    if cancelled_by_student:
        admin_ids = user_crud.get_all_admin_ids(db)
        if admin_ids:
            notification_crud.bulk_create_notifications(
                db,
                user_ids=admin_ids,
                type=NotificationTypeEnum.BOOKING_CANCELLED_BY_STUDENT,
                title="Booking Cancelled by Student",
                message=(
                    f"{booking.student.full_name} cancelled their booking for "
                    f"seat {seat_number}."
                ),
                link=f"/admin/bookings/{booking.id}",
                related_entity_type="booking",
                related_entity_id=booking.id,
            )


def notify_booking_expiring_soon(db, booking: Booking) -> None:
    notification_crud.create_notification(
        db,
        user_id=booking.student_id,
        type=NotificationTypeEnum.BOOKING_EXPIRING_SOON,
        title="Booking Expiring Soon",
        message=(
            f"Your booking for seat {booking.seat.seat_number} expires on "
            f"{booking.end_date.isoformat()}. Renew to keep your seat."
        ),
        link=f"/bookings/{booking.id}",
        related_entity_type="booking",
        related_entity_id=booking.id,
    )

    send_booking_expiry_reminder_email(
        to_email=booking.student.email,
        full_name=booking.student.full_name,
        seat_number=booking.seat.seat_number,
        end_date=booking.end_date,
    )


def notify_booking_expired(db, booking: Booking) -> None:
    notification_crud.create_notification(
        db,
        user_id=booking.student_id,
        type=NotificationTypeEnum.BOOKING_EXPIRED,
        title="Booking Expired",
        message=f"Your booking for seat {booking.seat.seat_number} has expired.",
        related_entity_type="booking",
        related_entity_id=booking.id,
    )


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------
def notify_payment_recorded(db, payment: Payment) -> None:
    notification_crud.create_notification(
        db,
        user_id=payment.student_id,
        type=NotificationTypeEnum.PAYMENT_RECORDED,
        title="Payment Received",
        message=(
            f"Payment of {payment.amount} {payment.currency} received via "
            f"{payment.method.value}."
        ),
        link=f"/payments/{payment.id}",
        related_entity_type="payment",
        related_entity_id=payment.id,
    )

    send_payment_confirmation_email(
        to_email=payment.student.email,
        full_name=payment.student.full_name,
        amount=payment.amount,
        currency=payment.currency,
        payment_date=payment.paid_at,
        transaction_ref=payment.transaction_ref,
    )


def notify_payment_due_soon(db, payment: Payment) -> None:
    notification_crud.create_notification(
        db,
        user_id=payment.student_id,
        type=NotificationTypeEnum.PAYMENT_DUE_SOON,
        title="Payment Due Soon",
        message=f"{payment.amount} {payment.currency} is due on {payment.due_date.isoformat()}.",
        link=f"/payments/{payment.id}",
        related_entity_type="payment",
        related_entity_id=payment.id,
    )

    send_payment_due_reminder_email(
        to_email=payment.student.email,
        full_name=payment.student.full_name,
        amount=payment.amount,
        currency=payment.currency,
        due_date=payment.due_date,
    )


def notify_payment_overdue(db, payment: Payment) -> None:
    notification_crud.create_notification(
        db,
        user_id=payment.student_id,
        type=NotificationTypeEnum.PAYMENT_OVERDUE,
        title="Payment Overdue",
        message=(
            f"{payment.amount} {payment.currency} was due on "
            f"{payment.due_date.isoformat()} and is now overdue."
        ),
        link=f"/payments/{payment.id}",
        related_entity_type="payment",
        related_entity_id=payment.id,
    )


def notify_payment_waived(db, payment: Payment) -> None:
    notification_crud.create_notification(
        db,
        user_id=payment.student_id,
        type=NotificationTypeEnum.PAYMENT_WAIVED,
        title="Payment Waived",
        message=(
            f"Your payment of {payment.amount} {payment.currency} has been "
            f"waived by the admin."
        ),
        link=f"/payments/{payment.id}",
        related_entity_type="payment",
        related_entity_id=payment.id,
    )


def notify_payment_refunded(db, payment: Payment) -> None:
    notification_crud.create_notification(
        db,
        user_id=payment.student_id,
        type=NotificationTypeEnum.PAYMENT_REFUNDED,
        title="Payment Refunded",
        message=f"Your payment of {payment.amount} {payment.currency} has been refunded.",
        link=f"/payments/{payment.id}",
        related_entity_type="payment",
        related_entity_id=payment.id,
    )


# ---------------------------------------------------------------------------
# Batch notification helpers (used after expire/overdue sweeps)
# ---------------------------------------------------------------------------
def notify_bookings_expired(db, bookings: list[Booking]) -> None:
    for booking in bookings:
        notify_booking_expired(db, booking)


def notify_payments_overdue(db, payments: list[Payment]) -> None:
    for payment in payments:
        notify_payment_overdue(db, payment)


# ---------------------------------------------------------------------------
# Admin broadcast
# ---------------------------------------------------------------------------
def broadcast(
    db,
    title: str,
    message: str,
    target: str,
    link: str | None = None,
    user_id: int | None = None,
) -> list:
    if target == "all_students":
        user_ids = user_crud.get_all_active_student_ids(db)
    elif target == "all_admins":
        user_ids = user_crud.get_all_admin_ids(db)
    elif target == "specific_user":
        user_ids = [user_id] if user_id is not None else []
    else:
        user_ids = []

    if not user_ids:
        return []

    return notification_crud.bulk_create_notifications(
        db,
        user_ids=user_ids,
        type=NotificationTypeEnum.GENERIC,
        title=title,
        message=message,
        link=link,
    )
