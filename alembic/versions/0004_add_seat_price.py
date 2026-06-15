"""add price column to seats

Revision ID: 0004_add_seat_price
Revises: 0003_create_bookings_table
Create Date: 2026-06-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_add_seat_price"
down_revision: Union[str, None] = "0003_create_bookings_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("seats") as batch_op:
        batch_op.add_column(sa.Column("price", sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("seats") as batch_op:
        batch_op.drop_column("price")
