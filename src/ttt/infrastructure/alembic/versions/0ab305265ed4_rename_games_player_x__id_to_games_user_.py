"""
rename `games.player{x}_id` to `games.user{x}_id`.

Revision ID: 0ab305265ed4
Revises: 3cbb0bf26e9e
Create Date: 2025-07-24 05:25:29.573399

"""

from collections.abc import Sequence

from alembic import op


revision: str = "0ab305265ed4"
down_revision: str | None = "3cbb0bf26e9e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE games RENAME CONSTRAINT
        games_player1_id_fkey
        TO games_user1_id_fkey;
    """)
    op.execute("""
        ALTER INDEX ix_games_player1_id RENAME
        TO ix_games_user1_id;
    """)
    op.alter_column(
        "games",
        "player1_id",
        new_column_name="user1_id",
    )

    op.execute("""
        ALTER TABLE games RENAME CONSTRAINT
        games_player2_id_fkey
        TO games_user2_id_fkey;
    """)
    op.execute("""
        ALTER INDEX ix_games_player2_id RENAME
        TO ix_games_user2_id;
    """)
    op.alter_column(
        "games",
        "player2_id",
        new_column_name="user2_id",
    )


def downgrade() -> None:
    op.execute("""
        ALTER TABLE games RENAME CONSTRAINT
        games_user1_id_fkey
        TO games_player1_id_fkey;
    """)
    op.execute("""
        ALTER INDEX ix_games_user1_id RENAME
        TO ix_games_player1_id;
    """)
    op.alter_column(
        "games",
        "user1_id",
        new_column_name="player1_id",
    )

    op.execute("""
        ALTER TABLE games RENAME CONSTRAINT
        games_user2_id_fkey
        TO games_player2_id_fkey;
    """)
    op.execute("""
        ALTER INDEX ix_games_user2_id RENAME
        TO ix_games_player2_id;
    """)
    op.alter_column(
        "games",
        "user2_id",
        new_column_name="player2_id",
    )
