"""
rename `players` to `users`.

Revision ID: 42ad1196c6da
Revises: 0ab305265ed4
Create Date: 2025-07-24 05:38:35.259138

"""
from collections.abc import Sequence

from alembic import op


revision: str = "42ad1196c6da"
down_revision: str | None = "0ab305265ed4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table("players", "users")


def downgrade() -> None:
    op.rename_table("users", "players")
