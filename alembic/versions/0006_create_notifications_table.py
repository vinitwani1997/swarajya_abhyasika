"""create notifications table

Revision ID: 0006_create_notifications_table
Revises: 0005_create_payments_table
Create Date: 2026-06-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0006_create_notifications_table"
down_revision: Union[str, None] = "0005_create_payments_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "registration_submitted",
                "account_approved",
                "account_rejected",
                "account_status_changed",
                "booking_confirmed",
                "booking_cancelled",
                "booking_expiring_soon",
                "booking_expired",
                "payment_recorded",
                "payment_due_soon",
                "payment_overdue",
                "payment_waived",
                "payment_refunded",
                "new_registration",
                "seat_booked",
                "booking_cancelled_by_student",
                "payment_overdue_alert",
                "generic",
                name="notificationtypeenum",
                native_enum=False,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("link", sa.String(length=255), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("related_entity_type", sa.String(length=30), nullable=True),
        sa.Column("related_entity_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_user_is_read", "notifications", ["user_id", "is_read"])
    op.create_index(
        "ix_notifications_user_created_at", "notifications", ["user_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_user_created_at", table_name="notifications")
    op.drop_index("ix_notifications_user_is_read", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
