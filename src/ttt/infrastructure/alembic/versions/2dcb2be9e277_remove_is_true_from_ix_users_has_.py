"""
remove `IS TRUE` from `ix_users_has_matchmaking_waiting`.

Revision ID: 2dcb2be9e277
Revises: 6642791b3bf8
Create Date: 2025-09-24 13:46:33.322702

"""

from collections.abc import Sequence

from alembic import op


revision: str = "2dcb2be9e277"
down_revision: str | None = "6642791b3bf8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(
        op.f("ix_users_has_matchmaking_waiting"),
        table_name="users",
        postgresql_where="(has_matchmaking_waiting IS TRUE)",
    )
    op.create_index(
        op.f("ix_users_has_matchmaking_waiting"),
        "users",
        ["has_matchmaking_waiting"],
        unique=False,
        postgresql_where="has_matchmaking_waiting",
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_users_has_matchmaking_waiting"), table_name="users")
    op.create_index(
        op.f("ix_users_has_matchmaking_waiting"),
        "users",
        ["has_matchmaking_waiting"],
        unique=False,
        postgresql_where="(has_matchmaking_waiting IS TRUE)",
    )
