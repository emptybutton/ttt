"""
rename `user_emojis.player_id` to `user_emojis.user_id`.

Revision ID: fde32a1982c7
Revises: e05971d2b8d5
Create Date: 2025-07-23 08:36:01.306514

"""

from collections.abc import Sequence

from alembic import op


revision: str = "fde32a1982c7"
down_revision: str | None = "e05971d2b8d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("user_emojis", "player_id", new_column_name="user_id")
    op.drop_index(op.f("ix_user_emojis_player_id"), table_name="user_emojis")
    op.create_index(
        op.f("ix_user_emojis_user_id"),
        "user_emojis",
        ["user_id"],
        unique=False,
    )
    op.drop_constraint(
        op.f("player_emojis_player_id_fkey"), "user_emojis", type_="foreignkey",
    )
    op.create_foreign_key(
        "player_emojis_user_id_fkey",
        "user_emojis",
        "players",
        ["user_id"],
        ["id"],
        initially="DEFERRED",
        deferrable=True,
    )


def downgrade() -> None:
    op.alter_column("user_emojis", "user_id", new_column_name="player_id")
    op.drop_index(op.f("ix_user_emojis_user_id"), table_name="user_emojis")
    op.create_index(
        op.f("ix_user_emojis_player_id"),
        "user_emojis",
        ["player_id"],
        unique=False,
    )
    op.drop_constraint(
        op.f("player_emojis_user_id_fkey"), "user_emojis", type_="foreignkey",
    )
    op.create_foreign_key(
        "player_emojis_player_id_fkey",
        "user_emojis",
        "players",
        ["user_id"],
        ["id"],
        initially="DEFERRED",
        deferrable=True,
    )
