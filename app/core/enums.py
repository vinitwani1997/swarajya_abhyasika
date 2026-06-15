import enum


class RoleEnum(str, enum.Enum):
    admin = "admin"
    student = "student"


class UserStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    active = "active"
    inactive = "inactive"


class SeatStatusEnum(str, enum.Enum):
    available = "available"
    occupied = "occupied"
    maintenance = "maintenance"
    inactive = "inactive"


class BookingStatusEnum(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"
    completed = "completed"


class PaymentStatusEnum(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"
    waived = "waived"
    refunded = "refunded"


class PaymentMethodEnum(str, enum.Enum):
    cash = "cash"
    upi = "upi"
    card = "card"
    bank_transfer = "bank_transfer"
    other = "other"


class NotificationTypeEnum(str, enum.Enum):
    # --- Student-facing ---
    REGISTRATION_SUBMITTED = "registration_submitted"
    ACCOUNT_APPROVED = "account_approved"
    ACCOUNT_REJECTED = "account_rejected"
    ACCOUNT_STATUS_CHANGED = "account_status_changed"
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    BOOKING_EXPIRING_SOON = "booking_expiring_soon"
    BOOKING_EXPIRED = "booking_expired"
    PAYMENT_RECORDED = "payment_recorded"
    PAYMENT_DUE_SOON = "payment_due_soon"
    PAYMENT_OVERDUE = "payment_overdue"
    PAYMENT_WAIVED = "payment_waived"
    PAYMENT_REFUNDED = "payment_refunded"

    # --- Admin-facing ---
    NEW_REGISTRATION = "new_registration"
    SEAT_BOOKED = "seat_booked"
    BOOKING_CANCELLED_BY_STUDENT = "booking_cancelled_by_student"
    PAYMENT_OVERDUE_ALERT = "payment_overdue_alert"

    # --- System / generic ---
    GENERIC = "generic"
