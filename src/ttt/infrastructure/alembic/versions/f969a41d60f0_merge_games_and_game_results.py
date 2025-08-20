"""
merge `games` and `game_results`.

Revision ID: f969a41d60f0
Revises: adfa1d5f22f4
Create Date: 2025-07-26 15:30:19.710374

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "f969a41d60f0"
down_revision: str | None = "adfa1d5f22f4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        UPDATE games SET
            result_cancelled_game_canceler_id = game_results.canceler_id,
            result_decided_game_user_win_user_id = game_results.win_winner_id,
            result_decided_game_user_win_new_stars = game_results.win_new_stars,
            result_decided_game_ai_win_ai_id = game_results.ai_win_ai_id
        FROM game_results
        WHERE game_results.game_id = games.id;
    """)

    op.drop_index(
        op.f("ix_game_results_ai_win_ai_id"), table_name="game_results",
    )
    op.drop_index(
        op.f("ix_game_results_canceler_id"), table_name="game_results",
    )
    op.drop_index(
        op.f("ix_game_results_win_winner_id"), table_name="game_results",
    )
    op.drop_table("game_results")
    sa.Enum("completed", "cancelled", name="game_result_type").drop(
        op.get_bind(),
    )


def downgrade() -> None:
    sa.Enum("completed", "cancelled", name="game_result_type").create(
        op.get_bind(),
    )
    op.create_table(
        "game_results",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("game_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "win_winner_id", sa.BIGINT(), autoincrement=False, nullable=True,
        ),
        sa.Column(
            "win_new_stars", sa.INTEGER(), autoincrement=False, nullable=True,
        ),
        sa.Column(
            "type",
            postgresql.ENUM(
                "completed",
                "cancelled",
                name="game_result_type",
                create_type=False,
            ),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "canceler_id", sa.BIGINT(), autoincrement=False, nullable=True,
        ),
        sa.Column(
            "ai_win_ai_id", sa.UUID(), autoincrement=False, nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["ai_win_ai_id"],
            ["ais.id"],
            name=op.f("game_results_ai_win_ai_id_fkey"),
            initially="DEFERRED",
            deferrable=True,
        ),
        sa.ForeignKeyConstraint(
            ["canceler_id"],
            ["users.id"],
            name=op.f("game_results_canceler_id_fkey"),
            initially="DEFERRED",
            deferrable=True,
        ),
        sa.ForeignKeyConstraint(
            ["game_id"],
            ["games.id"],
            name=op.f("game_results_game_id_fkey"),
            initially="DEFERRED",
            deferrable=True,
        ),
        sa.ForeignKeyConstraint(
            ["win_winner_id"],
            ["users.id"],
            name=op.f("game_results_winner_id_fkey"),
            initially="DEFERRED",
            deferrable=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("game_results_pkey")),
        sa.UniqueConstraint(
            "game_id",
            name=op.f("game_results_game_id_key"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )
    op.create_index(
        op.f("ix_game_results_win_winner_id"),
        "game_results",
        ["win_winner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_game_results_canceler_id"),
        "game_results",
        ["canceler_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_game_results_ai_win_ai_id"),
        "game_results",
        ["ai_win_ai_id"],
        unique=False,
    )

    op.execute("""
        INSERT INTO game_results(
            id,
            game_id,
            win_winner_id,
            win_new_stars,
            type,
            canceler_id,
            ai_win_ai_id
        )
        SELECT
            gen_random_uuid(),
            games.id,
            games.result_decided_game_user_win_user_id,
            games.result_decided_game_user_win_new_stars,
            CASE
                WHEN games.result_cancelled_game_canceler_id IS NOT NULL
                    THEN 'cancelled'::game_result_type
                WHEN (
                    result_draw_game_user_draw2_user_id IS NOT NULL
                    OR result_draw_game_ai_draw2_ai_id IS NOT NULL
                    OR result_draw_game_user_draw1_user_id IS NOT NULL
                    OR result_draw_game_ai_draw1_ai_id IS NOT NULL
                    OR result_decided_game_user_loss_user_id IS NOT NULL
                    OR result_decided_game_ai_loss_ai_id IS NOT NULL
                    OR result_decided_game_user_win_user_id IS NOT NULL
                    OR result_decided_game_ai_win_ai_id IS NOT NULL
                )
                    THEN 'completed'::game_result_type
                ELSE
                    NULL
            END,
            games.result_cancelled_game_canceler_id,
            games.result_decided_game_ai_win_ai_id
        FROM games
        WHERE games.state = 'completed';
    """)
