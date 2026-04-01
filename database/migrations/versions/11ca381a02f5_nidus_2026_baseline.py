"""nidus_2026_baseline

Revision ID: 11ca381a02f5
Revises:
Create Date: 2026-03-31 19:04:14.124195

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "11ca381a02f5"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "organization",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "user",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "role",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "scopes",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organization.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "member",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organization.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_organization_id"), "organization", ["id"], unique=False)
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    op.create_index(op.f("ix_role_id"), "role", ["id"], unique=False)
    op.create_index(op.f("ix_member_id"), "member", ["id"], unique=False)
    op.create_index(
        op.f("ix_member_organization_id"), "member", ["organization_id"], unique=False
    )
    op.create_index(op.f("ix_member_user_id"), "member", ["user_id"], unique=False)

    op.create_index(
        "ix_organization_slug_active",
        "organization",
        ["slug"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_user_email_active",
        "user",
        ["email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_role_name_active",
        "role",
        ["name", "organization_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.execute(
        "CREATE INDEX ix_role_scopes_gin ON role USING GIN (scopes jsonb_path_ops)"
    )

    op.execute("GRANT USAGE ON SCHEMA public TO nidus_app_user;")
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nidus_app_user;"
    )
    op.execute(
        "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nidus_app_user;"
    )

    tables_to_secure = ["organization", "member", "role", '"user"']
    for table in tables_to_secure:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")

    op.execute("""
        CREATE POLICY organization_isolation_policy ON organization
        AS PERMISSIVE FOR ALL TO nidus_app_user
        USING (
            (id::text = current_setting('app.current_organization_id', TRUE))
            OR (current_setting('app.current_organization_id', TRUE) = '') 
        ) WITH CHECK (true);
    """)

    for tenant_table in ["member", "role"]:
        op.execute(f"""
            CREATE POLICY {tenant_table}_isolation_policy ON {tenant_table}
            AS PERMISSIVE FOR ALL TO nidus_app_user
            USING (
                (organization_id::text = current_setting('app.current_organization_id', TRUE))
                OR (current_setting('app.current_organization_id', TRUE) = '')
            ) WITH CHECK (true);
        """)

    op.execute("""
        CREATE POLICY user_isolation_policy ON "user"
        AS PERMISSIVE FOR ALL TO nidus_app_user
        USING (
            (id::text = current_setting('app.current_user_id', TRUE))
            OR (current_setting('app.current_organization_id', TRUE) = '')
        ) WITH CHECK (true);
    """)


def downgrade() -> None:
    op.execute(
        "REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM nidus_app_user;"
    )
    op.execute("REVOKE USAGE ON SCHEMA public FROM nidus_app_user;")

    op.drop_table("member")
    op.drop_table("role")
    op.drop_table("user")
    op.drop_table("organization")
