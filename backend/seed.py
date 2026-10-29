"""
Nidus Core demo seed — multi-org sandbox for local / Docker.

Uses DATABASE_ADMIN_URL (bypasses RLS). Idempotent. Password: password123

  cd backend && uv run python seed.py
  docker compose exec api python seed.py
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.rls import clear_rls_context
from app.core.security import hash_password
from app.models import Member, Organization, User
from app.models.identity.invitation import Invitation
from app.models.identity.role import Role
from app.models.identity.scopes import DEFAULT_ROLES_CONFIG, DefaultRole, NidusScope

DEMO_PASSWORD = "password123"
HASHED_PASSWORD = hash_password(DEMO_PASSWORD)

ORGS: List[Dict[str, str]] = [
    {"name": "Acme Corp", "slug": "acme-corp"},
    {"name": "Nidus Labs", "slug": "nidus-labs"},
    {"name": "Beta Partners", "slug": "beta-partners"},
]

USERS: Dict[str, Dict[str, Any]] = {
    "owner@acme.dev": {"full_name": "Acme Owner"},
    "admin@acme.dev": {"full_name": "Acme Admin"},
    "member@acme.dev": {"full_name": "Acme Member"},
    "viewer@acme.dev": {"full_name": "Acme Viewer"},
    "owner@nidus.dev": {"full_name": "Nidus Owner"},
    "admin@nidus.dev": {"full_name": "Nidus Admin"},
    "member@nidus.dev": {"full_name": "Nidus Member"},
    "owner@beta.dev": {"full_name": "Beta Owner"},
    "viewer@beta.dev": {"full_name": "Beta Viewer"},
    "multi@nidus.dev": {"full_name": "Multi Org User"},
}

MEMBERSHIPS: List[tuple[str, str, str]] = [
    ("owner@acme.dev", "acme-corp", DefaultRole.OWNER),
    ("admin@acme.dev", "acme-corp", DefaultRole.ADMIN),
    ("member@acme.dev", "acme-corp", DefaultRole.MEMBER),
    ("viewer@acme.dev", "acme-corp", DefaultRole.VIEWER),
    ("multi@nidus.dev", "acme-corp", DefaultRole.OWNER),
    ("owner@nidus.dev", "nidus-labs", DefaultRole.OWNER),
    ("admin@nidus.dev", "nidus-labs", DefaultRole.ADMIN),
    ("member@nidus.dev", "nidus-labs", DefaultRole.MEMBER),
    ("multi@nidus.dev", "nidus-labs", DefaultRole.MEMBER),
    ("owner@beta.dev", "beta-partners", DefaultRole.OWNER),
    ("viewer@beta.dev", "beta-partners", DefaultRole.VIEWER),
]

PENDING_INVITES: List[tuple[str, str, str]] = [
    ("invitee@acme.dev", "acme-corp", DefaultRole.MEMBER),
    ("contractor@nidus.dev", "nidus-labs", DefaultRole.VIEWER),
    ("partner@beta.dev", "beta-partners", DefaultRole.ADMIN),
]

CUSTOM_ROLE = {
    "org_slug": "acme-corp",
    "name": "Billing Manager",
    "description": "Demo custom role with org read + audit read.",
    "scopes": [NidusScope.ORG_READ.value, NidusScope.AUDIT_READ.value],
}


def _admin_session_maker() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(str(settings.DATABASE_ADMIN_URL), pool_pre_ping=True)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def _get_or_create_org(session: AsyncSession, name: str, slug: str) -> Organization:
    OrgModel = cast(Any, Organization)
    existing = (
        await session.execute(select(Organization).where(OrgModel.slug == slug, OrgModel.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if existing:
        return existing

    org = Organization(name=name, slug=slug, is_active=True)
    session.add(org)
    await session.flush()
    return org


async def _ensure_default_roles(session: AsyncSession, org_id: UUID) -> Dict[str, Role]:
    RoleModel = cast(Any, Role)
    roles: Dict[str, Role] = {}

    for role_name, config in DEFAULT_ROLES_CONFIG.items():
        found = (
            await session.execute(
                select(Role).where(
                    RoleModel.organization_id == org_id,
                    RoleModel.name == role_name.value,
                    RoleModel.deleted_at.is_(None),
                )
            )
        ).scalar_one_or_none()

        if found:
            found.scopes = list(config["scopes"])
            found.description = config["description"]
            roles[role_name.value] = found
            continue

        role = Role(
            name=role_name.value,
            description=config["description"],
            scopes=list(config["scopes"]),
            organization_id=org_id,
        )
        session.add(role)
        await session.flush()
        roles[role_name.value] = role

    return roles


async def _get_or_create_user(session: AsyncSession, email: str, full_name: str) -> User:
    UserModel = cast(Any, User)
    existing = (
        await session.execute(select(User).where(UserModel.email == email, UserModel.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if existing:
        existing.full_name = full_name
        existing.hashed_password = HASHED_PASSWORD
        existing.is_active = True
        return existing

    user = User(
        email=email,
        full_name=full_name,
        hashed_password=HASHED_PASSWORD,
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    await session.flush()
    return user


async def _ensure_membership(
    session: AsyncSession,
    *,
    user_id: UUID,
    org_id: UUID,
    role_id: UUID,
) -> None:
    MemberModel = cast(Any, Member)
    existing = (
        await session.execute(
            select(Member).where(
                MemberModel.user_id == user_id,
                MemberModel.organization_id == org_id,
                MemberModel.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if existing:
        existing.role_id = role_id
        return

    session.add(Member(user_id=user_id, organization_id=org_id, role_id=role_id))


async def _ensure_custom_role(session: AsyncSession, org_id: UUID) -> Role:
    RoleModel = cast(Any, Role)
    name = CUSTOM_ROLE["name"]
    found = (
        await session.execute(
            select(Role).where(
                RoleModel.organization_id == org_id,
                RoleModel.name == name,
                RoleModel.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if found:
        found.description = CUSTOM_ROLE["description"]
        found.scopes = list(CUSTOM_ROLE["scopes"])
        return found

    role = Role(
        name=name,
        description=CUSTOM_ROLE["description"],
        scopes=list(CUSTOM_ROLE["scopes"]),
        organization_id=org_id,
    )
    session.add(role)
    await session.flush()
    return role


async def _ensure_pending_invite(
    session: AsyncSession,
    *,
    email: str,
    org_id: UUID,
    role_id: UUID,
) -> None:
    InvitationModel = cast(Any, Invitation)
    existing = (
        await session.execute(
            select(Invitation).where(
                InvitationModel.email == email,
                InvitationModel.organization_id == org_id,
                InvitationModel.is_accepted.is_(False),
                InvitationModel.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if existing:
        existing.role_id = role_id
        existing.expires_at = datetime.now(timezone.utc) + timedelta(days=14)
        return

    session.add(
        Invitation(
            email=email,
            organization_id=org_id,
            role_id=role_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=14),
            is_accepted=False,
        )
    )


def _print_summary() -> None:
    print("")
    print("=" * 72)
    print("Nidus Core demo seed ready")
    print(f"Password for all accounts: {DEMO_PASSWORD}")
    print("=" * 72)
    print("")
    print(f"{'Email':<28} {'Orgs / roles':<40}")
    print("-" * 72)
    by_email: Dict[str, List[str]] = {}
    for email, org_slug, role_name in MEMBERSHIPS:
        by_email.setdefault(email, []).append(f"{org_slug}:{role_name}")
    for email in sorted(by_email):
        print(f"{email:<28} {', '.join(by_email[email])}")
    print("")
    print("Pending invitations:")
    for email, org_slug, role_name in PENDING_INVITES:
        print(f"  - {email} -> {org_slug} as {role_name}")
    print("")
    print("Suggested logins:")
    print("  owner@acme.dev     full Owner + audit on Acme")
    print("  multi@nidus.dev    org picker (Acme Owner + Nidus Member)")
    print("  viewer@acme.dev    limited scopes (no members/roles/audit)")
    print("  admin@nidus.dev    Admin with audit:read on Nidus Labs")
    print("=" * 72)


async def seed_data() -> None:
    session_maker = _admin_session_maker()
    async with session_maker() as session:
        await clear_rls_context(session)

        orgs: Dict[str, Organization] = {}
        roles_by_org: Dict[str, Dict[str, Role]] = {}

        for spec in ORGS:
            org = await _get_or_create_org(session, spec["name"], spec["slug"])
            orgs[spec["slug"]] = org
            roles_by_org[spec["slug"]] = await _ensure_default_roles(session, org.id)

        await _ensure_custom_role(session, orgs[CUSTOM_ROLE["org_slug"]].id)

        users: Dict[str, User] = {}
        for email, meta in USERS.items():
            users[email] = await _get_or_create_user(session, email, meta["full_name"])

        for email, org_slug, role_name in MEMBERSHIPS:
            await _ensure_membership(
                session,
                user_id=users[email].id,
                org_id=orgs[org_slug].id,
                role_id=roles_by_org[org_slug][role_name].id,
            )

        for email, org_slug, role_name in PENDING_INVITES:
            await _ensure_pending_invite(
                session,
                email=email,
                org_id=orgs[org_slug].id,
                role_id=roles_by_org[org_slug][role_name].id,
            )

        await session.commit()

    _print_summary()


if __name__ == "__main__":
    asyncio.run(seed_data())
