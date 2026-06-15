"""create bookings table

Revision ID: 0003_create_bookings_table
Revises: 0002_create_seats_table
Create Date: 2026-06-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003_create_bookings_table"
down_revision: Union[str, None] = "0002_create_seats_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("seat_id", sa.Integer(), sa.ForeignKey("seats.id"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "expired",
                "cancelled",
                "completed",
                name="bookingstatusenum",
                native_enum=False,
                length=20,
            ),
            nullable=False,
            server_default="active",
        ),
        sa.Column("booking_type", sa.String(length=20), nullable=False, server_default="monthly"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_bookings_student_id", "bookings", ["student_id"])
    op.create_index("ix_bookings_seat_id", "bookings", ["seat_id"])
    op.create_index("ix_bookings_status", "bookings", ["status"])


def downgrade() -> None:
    op.drop_index("ix_bookings_status", table_name="bookings")
    op.drop_index("ix_bookings_seat_id", table_name="bookings")
    op.drop_index("ix_bookings_student_id", table_name="bookings")
    op.drop_table("bookings")
