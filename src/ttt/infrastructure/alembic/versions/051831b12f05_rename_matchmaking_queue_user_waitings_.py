"""
rename `matchmaking_queue_user_waitings` to `matchmaking_user_waitings`.

Revision ID: 051831b12f05
Revises: c122fc5b8ec6
Create Date: 2025-09-17 08:31:45.586302

"""

from collections.abc import Sequence

from alembic import op


revision: str = "051831b12f05"
down_revision: str | None = "c122fc5b8ec6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table(
        "matchmaking_queue_user_waitings", "matchmaking_user_waitings",
    )
    op.execute("""
        ALTER INDEX ix_matchmaking_queue_user_waitings_user_id
            RENAME TO ix_matchmaking_user_waitings_user_id
    """)
    op.execute("""
        ALTER INDEX matchmaking_queue_user_waitings_pkey
            RENAME TO matchmaking_user_waitings_pkey
    """)
    op.execute("""
        ALTER TABLE matchmaking_user_waitings
            RENAME CONSTRAINT matchmaking_queue_user_waitings_user_id_fkey
            TO matchmaking_user_waitings_user_id_fkey
    """)


def downgrade() -> None:
    op.rename_table(
        "matchmaking_user_waitings", "matchmaking_queue_user_waitings",
    )
    op.execute("""
        ALTER INDEX ix_matchmaking_user_waitings_user_id
            RENAME TO ix_matchmaking_queue_user_waitings_user_id
    """)
    op.execute("""
        ALTER INDEX matchmaking_user_waitings_pkey
            RENAME TO matchmaking_queue_user_waitings_pkey
    """)
    op.execute("""
        ALTER TABLE matchmaking_queue_user_waitings
            RENAME CONSTRAINT matchmaking_user_waitings_user_id_fkey
            TO matchmaking_queue_user_waitings_user_id_fkey
    """)
