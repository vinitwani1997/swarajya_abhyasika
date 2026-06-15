import logging
import smtplib
from datetime import date, datetime
from decimal import Decimal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str, html: bool = False) -> bool:
    """Send an email via SMTP. If SMTP is not configured, logs the email
    instead (useful for local development before SMTP credentials exist).

    Returns True if the email was sent (or logged) successfully.
    """
    if not settings.SMTP_HOST or not settings.SMTP_USERNAME:
        logger.info(
            "SMTP not configured. Email not sent.\nTo: %s\nSubject: %s\nBody:\n%s",
            to_email,
            subject,
            body,
        )
        return True

    message = MIMEMultipart()
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html" if html else "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False


def send_credentials_email(to_email: str, full_name: str, user_id: str, password: str) -> bool:
    subject = "Your Library Account Has Been Approved"
    body = (
        f"Hi {full_name},\n\n"
        f"Your library account has been approved and activated.\n\n"
        f"You can now log in using the following credentials:\n"
        f"User ID: {user_id}\n"
        f"Password: {password}\n\n"
        f"Please log in and consider changing your password.\n\n"
        f"Regards,\n{settings.SMTP_FROM_NAME}"
    )
    return send_email(to_email, subject, body)


def send_booking_confirmation_email(
    to_email: str, full_name: str, seat_number: str, start_date: date, end_date: date
) -> bool:
    subject = "Library Seat Booking Confirmation"
    body = (
        f"Hi {full_name},\n\n"
        f"Your seat booking has been confirmed.\n\n"
        f"Seat Number: {seat_number}\n"
        f"Start Date: {start_date.isoformat()}\n"
        f"End Date: {end_date.isoformat()}\n\n"
        f"Please carry a valid ID when visiting the library.\n\n"
        f"Regards,\n{settings.SMTP_FROM_NAME}"
    )
    return send_email(to_email, subject, body)


def send_payment_confirmation_email(
    to_email: str,
    full_name: str,
    amount: Decimal,
    currency: str,
    payment_date: datetime | None,
    transaction_ref: str | None,
) -> bool:
    subject = "Payment Received - Library Fee"
    paid_on = payment_date.strftime("%Y-%m-%d %H:%M") if payment_date else "N/A"
    ref_line = f"Transaction Reference: {transaction_ref}\n" if transaction_ref else ""
    body = (
        f"Hi {full_name},\n\n"
        f"We have received your payment. Here are the details:\n\n"
        f"Amount: {amount} {currency}\n"
        f"Date: {paid_on}\n"
        f"{ref_line}\n"
        f"Thank you for your payment.\n\n"
        f"Regards,\n{settings.SMTP_FROM_NAME}"
    )
    return send_email(to_email, subject, body)


def send_payment_due_reminder_email(
    to_email: str, full_name: str, amount: Decimal, currency: str, due_date: date
) -> bool:
    subject = "Payment Reminder - Library Fee Due Soon"
    body = (
        f"Hi {full_name},\n\n"
        f"This is a reminder that a payment of {amount} {currency} is due on "
        f"{due_date.isoformat()}.\n\n"
        f"Please make the payment at the library desk to avoid service "
        f"interruption.\n\n"
        f"Regards,\n{settings.SMTP_FROM_NAME}"
    )
    return send_email(to_email, subject, body)


def send_booking_expiry_reminder_email(
    to_email: str, full_name: str, seat_number: str, end_date: date
) -> bool:
    subject = "Library Seat Booking Expiring Soon"
    body = (
        f"Hi {full_name},\n\n"
        f"Your booking for seat {seat_number} is expiring on {end_date.isoformat()}.\n\n"
        f"Please visit the library desk to renew your booking if you'd like "
        f"to continue using the seat.\n\n"
        f"Regards,\n{settings.SMTP_FROM_NAME}"
    )
    return send_email(to_email, subject, body)
