"""
add `state` to `payments` table.

Revision ID: 1dd1ac771b91
Revises: ce3ee64d0d3b
Create Date: 2025-07-02 05:32:15.368212

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "1dd1ac771b91"
down_revision: str | None = "ce3ee64d0d3b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    sa.Enum(
        "in_process",
        "cancelled",
        "completed",
        name="payment_state",
    ).create(op.get_bind())

    op.add_column(
        "payments",
        sa.Column(
            "state",
            postgresql.ENUM(
                "in_process",
                "cancelled",
                "completed",
                name="payment_state",
                create_type=False,
            ),
            nullable=True,
        ),
    )

    op.execute("""
        UPDATE payments SET state = 'cancelled' WHERE is_cancelled;
    """)
    op.execute("""
        UPDATE payments SET state = 'completed' WHERE success_id IS NOT NULL;
    """)
    op.execute("""
        UPDATE payments SET state = 'in_process'
        WHERE NOT is_cancelled AND success_id IS NULL;
    """)

    op.drop_column("payments", "is_cancelled")
    op.alter_column("payments", "state", nullable=False)


def downgrade() -> None:
    op.add_column(
        "payments",
        sa.Column(
            "is_cancelled", sa.BOOLEAN(), autoincrement=False, nullable=True,
        ),
    )
    op.execute("""
        UPDATE payments SET is_cancelled = true WHERE state = 'cancelled';
    """)
    op.alter_column("payments", "is_cancelled", nullable=False)

    op.drop_column("payments", "state")
