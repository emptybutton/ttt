"""
rename `cells.filler_id` to `cells.user_filler_id`.

Revision ID: 3cbb0bf26e9e
Revises: 3f0d6b39f862
Create Date: 2025-07-24 05:21:06.119116

"""

from collections.abc import Sequence

from alembic import op


revision: str = "3cbb0bf26e9e"
down_revision: str | None = "3f0d6b39f862"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE cells RENAME CONSTRAINT
        cells_filler_id_fkey
        TO cells_user_filler_id_fkey;
    """)
    op.execute("""
        ALTER INDEX ix_cells_filler_id RENAME
        TO ix_cells_user_filler_id;
    """)
    op.alter_column(
        "cells",
        "filler_id",
        new_column_name="user_filler_id",
    )


def downgrade() -> None:
    op.execute("""
        ALTER TABLE cells RENAME CONSTRAINT
        cells_user_filler_id_fkey
        TO cells_filler_id_fkey;
    """)
    op.execute("""
        ALTER INDEX ix_cells_user_filler_id RENAME
        TO ix_cells_filler_id;
    """)
    op.alter_column(
        "cells",
        "user_filler_id",
        new_column_name="filler_id",
    )
