"""
rename `players` constrains to `users` constrains.

Revision ID: fb04714a84d4
Revises: 42ad1196c6da
Create Date: 2025-07-24 05:40:57.564599

"""
from collections.abc import Sequence

from alembic import op


revision: str = "fb04714a84d4"
down_revision: str | None = "42ad1196c6da"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER INDEX players_pkey RENAME TO users_pkey;")
    op.execute("""
        ALTER INDEX ix_players_game_location_game_id
        RENAME TO ix_users_game_location_game_id;
    """)
    op.execute("""
        ALTER INDEX ix_players_selected_emoji_id
        RENAME TO ix_users_selected_emoji_id;
    """)

    op.execute("""
        ALTER TABLE users RENAME CONSTRAINT
        players_game_location_game_id_fkey TO users_game_location_game_id_fkey;
    """)
    op.execute("""
        ALTER TABLE users RENAME CONSTRAINT
        players_selected_emoji_id_fkey TO users_selected_emoji_id_fkey;
    """)


def downgrade() -> None:
    op.execute("ALTER INDEX users_pkey RENAME TO players_pkey;")
    op.execute("""
        ALTER INDEX ix_users_game_location_game_id
        RENAME TO ix_players_game_location_game_id;
    """)
    op.execute("""
        ALTER INDEX ix_users_selected_emoji_id
        RENAME TO ix_players_selected_emoji_id;
    """)

    op.execute("""
        ALTER TABLE users RENAME CONSTRAINT
        users_game_location_game_id_fkey TO players_game_location_game_id_fkey;
    """)
    op.execute("""
        ALTER TABLE users RENAME CONSTRAINT
        users_selected_emoji_id_fkey TO players_selected_emoji_id_fkey;
    """)
