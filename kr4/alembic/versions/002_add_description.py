"""add description to products

Revision ID: 002
Revises: 001
Create Date: 2026-05-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite плохо меняет nullable, добавляем сразу NOT NULL и значением по умолчанию
    op.add_column(
        "products",
        sa.Column(
            "description",
            sa.String(length=500),
            nullable=False,
            server_default="no description",
        ),
    )


def downgrade() -> None:
    op.drop_column("products", "description")
