"""refactor_tenant_to_organization

Revision ID: 33518611acde
Revises:
Create Date: 2026-03-28 17:56:11.796068

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "33518611acde"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE tenants RENAME TO organization")

    try:
        op.execute("ALTER INDEX ix_tenants_name RENAME TO ix_organization_name")
    except Exception:
        pass

    op.execute("ALTER TABLE organization ADD COLUMN IF NOT EXISTS slug VARCHAR")
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true"
    )
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', CURRENT_TIMESTAMP)"
    )
    op.execute(
        "ALTER TABLE organization ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', CURRENT_TIMESTAMP)"
    )
    op.execute(
        "UPDATE organization SET slug = LOWER(REPLACE(name, ' ', '-')) WHERE slug IS NULL"
    )
    op.execute("ALTER TABLE organization ALTER COLUMN slug SET NOT NULL")
    op.execute("ALTER TABLE organization ALTER COLUMN is_active SET NOT NULL")
    op.execute("ALTER TABLE organization ALTER COLUMN created_at SET NOT NULL")
    op.execute("ALTER TABLE organization ALTER COLUMN updated_at SET NOT NULL")
    op.create_index(op.f("ix_organization_slug"), "organization", ["slug"], unique=True)

    op.create_table(
        "role",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "user",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "member",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organization.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("member")
    op.drop_table("user")
    op.drop_table("role")

    op.drop_index(op.f("ix_organization_slug"), table_name="organization")
    op.drop_column("organization", "is_active")
    op.drop_column("organization", "slug")

    op.execute("ALTER INDEX ix_organization_name RENAME TO ix_tenants_name")
    op.rename_table("organization", "tenants")
