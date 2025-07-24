"""
rename `player_emojis_user_id_fkey` to `user_emojis_user_id_fkey`.

Revision ID: 50990aed76a8
Revises: 274a1fc84d0c
Create Date: 2025-07-23 08:54:03.378941

"""

from collections.abc import Sequence

from alembic import op


revision: str = "50990aed76a8"
down_revision: str | None = "274a1fc84d0c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE user_emojis RENAME CONSTRAINT
        player_emojis_user_id_fkey TO user_emojis_user_id_fkey;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE user_emojis RENAME CONSTRAINT
        user_emojis_user_id_fkey TO player_emojis_user_id_fkey;
    """)
