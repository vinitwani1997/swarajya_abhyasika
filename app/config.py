from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Project
    PROJECT_NAME: str = "Library Seat Booking System"
    ENV: str = "dev"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./library.db"

    # JWT / Security
    SECRET_KEY: str = "change-this-to-a-long-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # SMTP / Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "Library Management System"
    SMTP_USE_TLS: bool = True

    # Initial Admin Seeding
    ADMIN_FULL_NAME: str = "Super Admin"
    ADMIN_EMAIL: str = "admin@library.com"
    ADMIN_PASSWORD: str = "ChangeMe123!"

    # Pricing / Payments
    # Used as a fallback when a seat has no specific `price` set.
    DEFAULT_MONTHLY_SEAT_FEE: float = 1000.0
    PAYMENT_CURRENCY: str = "INR"
    PAYMENT_DUE_GRACE_DAYS: int = 3

    # Reminders (days before expiry/due date to send reminder emails)
    REMINDER_DAYS_BEFORE: int = 3

    # Scheduler
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_HOUR: int = 1  # hour of day (24h) the daily job runs
    SCHEDULER_MINUTE: int = 0


settings = Settings()
