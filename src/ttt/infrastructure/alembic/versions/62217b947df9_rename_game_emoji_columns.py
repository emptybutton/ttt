"""
rename game emoji columns.

Revision ID: 62217b947df9
Revises: 1106a6a301dc
Create Date: 2025-06-22 15:11:35.209641

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "62217b947df9"
down_revision: str | None = "1106a6a301dc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "games",
        "player1_emoji_char",
        new_column_name="player1_emoji_str",
    )
    op.alter_column(
        "games",
        "player2_emoji_char",
        new_column_name="player2_emoji_str",
    )


def downgrade() -> None:
    op.alter_column(
        "games",
        "player1_emoji_str",
        new_column_name="player1_emoji_char",
    )
    op.alter_column(
        "games",
        "player2_emoji_str",
        new_column_name="player2_emoji_char",
    )
