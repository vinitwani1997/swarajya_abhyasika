"""create payments table

Revision ID: 0005_create_payments_table
Revises: 0004_add_seat_price
Create Date: 2026-06-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005_create_payments_table"
down_revision: Union[str, None] = "0004_add_seat_price"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id"), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="INR"),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "paid",
                "overdue",
                "waived",
                "refunded",
                name="paymentstatusenum",
                native_enum=False,
                length=20,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "method",
            sa.Enum(
                "cash",
                "upi",
                "card",
                "bank_transfer",
                "other",
                name="paymentmethodenum",
                native_enum=False,
                length=20,
            ),
            nullable=True,
        ),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("recorded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("transaction_ref", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_payments_student_id", "payments", ["student_id"])
    op.create_index("ix_payments_booking_id", "payments", ["booking_id"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_due_date", "payments", ["due_date"])


def downgrade() -> None:
    op.drop_index("ix_payments_due_date", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_booking_id", table_name="payments")
    op.drop_index("ix_payments_student_id", table_name="payments")
    op.drop_table("payments")
