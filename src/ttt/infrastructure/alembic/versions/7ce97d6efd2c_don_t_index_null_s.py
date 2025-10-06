"""
don't index `null`s.

Revision ID: 7ce97d6efd2c
Revises: ba0f7132baef
Create Date: 2025-09-19 11:58:53.188572

"""

from collections.abc import Sequence

from alembic import op


revision: str = "7ce97d6efd2c"
down_revision: str | None = "ba0f7132baef"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(op.f("ix_users_selected_emoji_id"), table_name="users")
    op.create_index(
        op.f("ix_users_selected_emoji_id"),
        "users",
        ["selected_emoji_id"],
        unique=False,
        postgresql_where="(selected_emoji_id IS NOT NULL)",
    )

    op.drop_index(op.f("ix_users_current_game_id"), table_name="users")
    op.create_index(
        op.f("ix_users_current_game_id"),
        "users",
        ["current_game_id"],
        unique=False,
        postgresql_where="(current_game_id IS NOT NULL)",
    )

    op.drop_index(op.f("ix_cells_user_filler_id"), table_name="cells")
    op.create_index(
        op.f("ix_cells_user_filler_id"),
        "cells",
        ["user_filler_id"],
        unique=False,
        postgresql_where="(user_filler_id IS NOT NULL)",
    )

    op.drop_index(op.f("ix_cells_ai_filler_id"), table_name="cells")
    op.create_index(
        op.f("ix_cells_ai_filler_id"),
        "cells",
        ["ai_filler_id"],
        unique=False,
        postgresql_where="(ai_filler_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_users_selected_emoji_id"), table_name="users")
    op.create_index(
        op.f("ix_users_selected_emoji_id"),
        "users",
        ["selected_emoji_id"],
        unique=False,
    )

    op.drop_index(op.f("ix_users_current_game_id"), table_name="users")
    op.create_index(
        op.f("ix_users_current_game_id"),
        "users",
        ["current_game_id"],
        unique=False,
    )

    op.drop_index(op.f("ix_cells_user_filler_id"), table_name="cells")
    op.create_index(
        op.f("ix_cells_user_filler_id"),
        "cells",
        ["user_filler_id"],
        unique=False,
    )

    op.drop_index(op.f("ix_cells_ai_filler_id"), table_name="cells")
    op.create_index(
        op.f("ix_cells_ai_filler_id"),
        "cells",
        ["ai_filler_id"],
        unique=False,
    )
