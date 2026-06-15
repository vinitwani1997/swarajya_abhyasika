import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.database import SessionLocal
from app.crud import booking as booking_crud
from app.crud import payment as payment_crud
from app.services import notification_service

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def run_daily_jobs() -> None:
    """Run all daily maintenance jobs: expire overdue bookings/payments and
    send reminder notifications (in-app + email) for items due/expiring soon."""
    db = SessionLocal()
    try:
        expired_bookings = booking_crud.expire_overdue_bookings(db)
        if expired_bookings:
            notification_service.notify_bookings_expired(db, expired_bookings)
            logger.info("Expired %d overdue booking(s).", len(expired_bookings))

        overdue_payments = payment_crud.mark_overdue_payments(db)
        if overdue_payments:
            notification_service.notify_payments_overdue(db, overdue_payments)
            logger.info("Marked %d payment(s) as overdue.", len(overdue_payments))

        _send_booking_expiry_reminders(db)
        _send_payment_due_reminders(db)
    except Exception:
        logger.exception("Error running daily scheduled jobs")
    finally:
        db.close()


def _send_booking_expiry_reminders(db) -> None:
    bookings = booking_crud.get_bookings_ending_in_days(db, settings.REMINDER_DAYS_BEFORE)
    for booking in bookings:
        notification_service.notify_booking_expiring_soon(db, booking)
    if bookings:
        logger.info("Sent %d booking expiry reminder(s).", len(bookings))


def _send_payment_due_reminders(db) -> None:
    payments = payment_crud.get_payments_due_in_days(db, settings.REMINDER_DAYS_BEFORE)
    for payment in payments:
        notification_service.notify_payment_due_soon(db, payment)
    if payments:
        logger.info("Sent %d payment due reminder(s).", len(payments))


def start() -> None:
    global _scheduler

    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler disabled via settings.SCHEDULER_ENABLED=False.")
        return

    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        run_daily_jobs,
        trigger="cron",
        hour=settings.SCHEDULER_HOUR,
        minute=settings.SCHEDULER_MINUTE,
        id="daily_library_jobs",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "Scheduler started. Daily jobs run at %02d:%02d.",
        settings.SCHEDULER_HOUR,
        settings.SCHEDULER_MINUTE,
    )


def shutdown() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped.")
