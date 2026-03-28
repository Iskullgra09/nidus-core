"""Enable RLS for tenants

Revision ID: d99451053c8c
Revises: 9d69e3f023a5
Create Date: 2026-03-28 13:10:40.757712

"""

from typing import Sequence, Union

import sqlalchemy as sa  # noqa: F401 # type: ignore
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d99451053c8c"
down_revision: Union[str, Sequence[str], None] = "9d69e3f023a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable and Force RLS on the table
    op.execute("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE tenants FORCE ROW LEVEL SECURITY;")

    # 2. Create the isolation policy
    # We use NULLIF to safely handle cases where the setting is completely missing
    op.execute("""
        CREATE POLICY tenant_isolation_policy ON tenants
        FOR ALL
        USING (id = NULLIF(current_setting('nidus.current_tenant_id', TRUE), '')::uuid);
    """)


def downgrade() -> None:
    # Rollback instructions
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON tenants;")
    op.execute("ALTER TABLE tenants NO FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE tenants DISABLE ROW LEVEL SECURITY;")
