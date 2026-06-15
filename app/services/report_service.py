from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import (
    BookingStatusEnum,
    PaymentStatusEnum,
    RoleEnum,
    SeatStatusEnum,
    UserStatusEnum,
)
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.seat import Seat
from app.models.user import User
from app.schemas.report import (
    BookingStatsReport,
    OccupancyReport,
    RevenueReport,
    StudentGrowthReport,
)


def _count_seats_by_status(db: Session, status: SeatStatusEnum) -> int:
    return db.execute(
        select(func.count()).select_from(Seat).where(Seat.status == status)
    ).scalar_one()


def get_occupancy_report(db: Session) -> OccupancyReport:
    total_seats = db.execute(select(func.count()).select_from(Seat)).scalar_one()

    available = _count_seats_by_status(db, SeatStatusEnum.available)
    occupied = _count_seats_by_status(db, SeatStatusEnum.occupied)
    maintenance = _count_seats_by_status(db, SeatStatusEnum.maintenance)
    inactive = _count_seats_by_status(db, SeatStatusEnum.inactive)

    occupancy_rate = (occupied / total_seats * 100) if total_seats else 0.0

    return OccupancyReport(
        total_seats=total_seats,
        available=available,
        occupied=occupied,
        maintenance=maintenance,
        inactive=inactive,
        occupancy_rate_percent=round(occupancy_rate, 2),
    )


def _sum_payments(db: Session, status: PaymentStatusEnum, start_date, end_date):
    query = select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == status)
    if start_date is not None:
        query = query.where(Payment.due_date >= start_date)
    if end_date is not None:
        query = query.where(Payment.due_date <= end_date)
    return db.execute(query).scalar_one()


def get_revenue_report(
    db: Session, start_date: date | None = None, end_date: date | None = None
) -> RevenueReport:
    total_collected = _sum_payments(db, PaymentStatusEnum.paid, start_date, end_date)
    total_pending = _sum_payments(db, PaymentStatusEnum.pending, start_date, end_date)
    total_overdue = _sum_payments(db, PaymentStatusEnum.overdue, start_date, end_date)
    total_waived = _sum_payments(db, PaymentStatusEnum.waived, start_date, end_date)
    total_refunded = _sum_payments(db, PaymentStatusEnum.refunded, start_date, end_date)

    return RevenueReport(
        start_date=start_date,
        end_date=end_date,
        total_collected=total_collected,
        total_pending=total_pending,
        total_overdue=total_overdue,
        total_waived=total_waived,
        total_refunded=total_refunded,
    )


def _count_users_by_status(db: Session, status: UserStatusEnum, role_filter=None) -> int:
    query = select(func.count()).select_from(User).where(User.status == status)
    if role_filter is not None:
        query = query.where(User.role == role_filter)
    return db.execute(query).scalar_one()


def get_student_growth_report(
    db: Session, start_date: date | None = None, end_date: date | None = None
) -> StudentGrowthReport:
    total_students = db.execute(
        select(func.count()).select_from(User).where(User.role == RoleEnum.student)
    ).scalar_one()

    pending = _count_users_by_status(db, UserStatusEnum.pending, RoleEnum.student)
    active = _count_users_by_status(db, UserStatusEnum.active, RoleEnum.student)
    inactive = _count_users_by_status(db, UserStatusEnum.inactive, RoleEnum.student)
    rejected = _count_users_by_status(db, UserStatusEnum.rejected, RoleEnum.student)

    query = select(func.count()).select_from(User).where(User.role == RoleEnum.student)
    if start_date is not None:
        query = query.where(User.created_at >= start_date)
    if end_date is not None:
        query = query.where(User.created_at <= end_date)
    new_registrations = db.execute(query).scalar_one()

    return StudentGrowthReport(
        total_students=total_students,
        pending_approval=pending,
        active=active,
        inactive=inactive,
        rejected=rejected,
        new_registrations_in_range=new_registrations,
        start_date=start_date,
        end_date=end_date,
    )


def _count_bookings_by_status(db: Session, status: BookingStatusEnum) -> int:
    return db.execute(
        select(func.count()).select_from(Booking).where(Booking.status == status)
    ).scalar_one()


def get_booking_stats_report(db: Session) -> BookingStatsReport:
    active = _count_bookings_by_status(db, BookingStatusEnum.active)
    expired = _count_bookings_by_status(db, BookingStatusEnum.expired)
    cancelled = _count_bookings_by_status(db, BookingStatusEnum.cancelled)

    target_date = date.today() + timedelta(days=settings.REMINDER_DAYS_BEFORE)
    expiring_soon = db.execute(
        select(func.count())
        .select_from(Booking)
        .where(Booking.status == BookingStatusEnum.active, Booking.end_date <= target_date)
    ).scalar_one()

    total_bookings = active + expired + cancelled
    cancellation_rate = (cancelled / total_bookings * 100) if total_bookings else 0.0

    return BookingStatsReport(
        active_bookings=active,
        expired_bookings=expired,
        cancelled_bookings=cancelled,
        expiring_soon=expiring_soon,
        cancellation_rate_percent=round(cancellation_rate, 2),
    )
