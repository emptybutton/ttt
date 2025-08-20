"""
rename `player_emojis_pkey` to `user_emojis_pkey`.

Revision ID: 274a1fc84d0c
Revises: fde32a1982c7
Create Date: 2025-07-23 08:45:07.054035

"""

from collections.abc import Sequence

from alembic import op


revision: str = "274a1fc84d0c"
down_revision: str | None = "fde32a1982c7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE user_emojis
        RENAME CONSTRAINT player_emojis_pkey TO user_emojis_pkey;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE user_emojis
        RENAME CONSTRAINT user_emojis_pkey TO player_emojis_pkey;
    """)
