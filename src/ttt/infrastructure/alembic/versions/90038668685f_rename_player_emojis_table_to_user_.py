"""
rename `player_emojis` table to `user_emojis`.

Revision ID: 90038668685f
Revises: 1dd1ac771b91
Create Date: 2025-07-18 06:11:02.612879

"""

from collections.abc import Sequence

from alembic import op


revision: str = "90038668685f"
down_revision: str | None = "1dd1ac771b91"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        op.f("players_selected_emoji_id_fkey"),
        "players",
        type_="foreignkey",
    )
    op.rename_table("player_emojis", "user_emojis")
    op.create_foreign_key(
        "players_selected_emoji_id_fkey",
        "players",
        "user_emojis",
        ["selected_emoji_id"],
        ["id"],
        initially="DEFERRED",
        deferrable=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("players_selected_emoji_id_fkey"),
        "players",
        type_="foreignkey",
    )
    op.rename_table("user_emojis", "player_emojis")
    op.create_foreign_key(
        "players_selected_emoji_id_fkey",
        "players",
        "player_emojis",
        ["selected_emoji_id"],
        ["id"],
        initially="DEFERRED",
        deferrable=True,
    )
