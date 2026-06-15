"""create seats table

Revision ID: 0002_create_seats_table
Revises: 0001_create_users_table
Create Date: 2026-06-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_create_seats_table"
down_revision: Union[str, None] = "0001_create_users_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "seats",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("seat_number", sa.String(length=20), nullable=False),
        sa.Column("floor", sa.String(length=50), nullable=True),
        sa.Column("zone", sa.String(length=50), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "available",
                "occupied",
                "maintenance",
                "inactive",
                name="seatstatusenum",
                native_enum=False,
                length=20,
            ),
            nullable=False,
            server_default="available",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_seats_seat_number", "seats", ["seat_number"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_seats_seat_number", table_name="seats")
    op.drop_table("seats")
