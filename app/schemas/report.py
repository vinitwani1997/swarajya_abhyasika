from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class OccupancyReport(BaseModel):
    total_seats: int
    available: int
    occupied: int
    maintenance: int
    inactive: int
    occupancy_rate_percent: float


class RevenueReport(BaseModel):
    start_date: date | None
    end_date: date | None
    total_collected: Decimal
    total_pending: Decimal
    total_overdue: Decimal
    total_waived: Decimal
    total_refunded: Decimal


class StudentGrowthReport(BaseModel):
    total_students: int
    pending_approval: int
    active: int
    inactive: int
    rejected: int
    new_registrations_in_range: int
    start_date: date | None
    end_date: date | None


class BookingStatsReport(BaseModel):
    active_bookings: int
    expired_bookings: int
    cancelled_bookings: int
    expiring_soon: int  # within REMINDER_DAYS_BEFORE days
    cancellation_rate_percent: float
