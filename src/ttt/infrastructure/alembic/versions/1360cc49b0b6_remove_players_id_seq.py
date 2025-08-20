"""
remove `players_id_seq`.

Revision ID: 1360cc49b0b6
Revises: fb04714a84d4
Create Date: 2025-07-24 05:50:47.308411

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "1360cc49b0b6"
down_revision: str | None = "fb04714a84d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN id DROP DEFAULT;")
    op.execute("DROP SEQUENCE players_id_seq;")


def downgrade() -> None:
    connection = op.get_bind()

    max_user_id: int = connection.scalar(sa.text("SELECT max(id) from users;"))
    sequence_start = max_user_id + 1000
    op.execute(f"CREATE SEQUENCE players_id_seq START WITH {sequence_start};")

    op.execute("""
        ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('players_id_seq');
    """)
