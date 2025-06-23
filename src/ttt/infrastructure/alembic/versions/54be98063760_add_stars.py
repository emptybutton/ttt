"""
add stars.

Revision ID: 54be98063760
Revises: fa2086ce276b
Create Date: 2025-06-23 04:56:57.515387

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "54be98063760"
down_revision: str | None = "fa2086ce276b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "game_results",
        "winner_id",
        new_column_name="win_winner_id",
    )
    op.add_column(
        "game_results", sa.Column("win_new_stars", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.alter_column(
        "game_results",
        "win_winner_id",
        new_column_name="winner_id",
    )
    op.drop_column("game_results", "win_new_stars")
