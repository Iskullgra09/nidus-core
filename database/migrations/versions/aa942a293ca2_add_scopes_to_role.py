# type: ignore
"""add_scopes_to_role

Revision ID: aa942a293ca2
Revises: ee0e2f880b1e
Create Date: 2026-03-31 11:37:49.665537
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "aa942a293ca2"
down_revision: Union[str, Sequence[str], None] = "ee0e2f880b1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "role",
        sa.Column(
            "scopes",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
    )

    op.execute(
        "CREATE INDEX ix_role_scopes_gin ON role USING GIN (scopes jsonb_path_ops)"
    )


def downgrade() -> None:
    op.drop_index("ix_role_scopes_gin", table_name="role")
    op.drop_column("role", "scopes")
