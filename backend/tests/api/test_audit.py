import uuid
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditAction, AuditLog
from app.models.identity.scopes import NidusScope


@pytest.mark.asyncio
async def test_onboarding_and_login_write_audit_events(
    auth_client: tuple[AsyncClient, dict[str, Any]],
    admin_db_session: AsyncSession,
) -> None:
    client, meta = auth_client
    org_id = uuid.UUID(str(meta["org_id"]))

    result = await admin_db_session.execute(
        select(AuditLog).where(AuditLog.organization_id == org_id).order_by(AuditLog.id.desc())
    )
    actions = {row.action for row in result.scalars().all()}
    assert AuditAction.ORG_CREATE.value in actions
    assert AuditAction.AUTH_LOGIN.value in actions

    res = await client.get("/api/v1/audit-logs")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert len(body["data"]["items"]) >= 2
    listed_actions = {item["action"] for item in body["data"]["items"]}
    assert AuditAction.ORG_CREATE.value in listed_actions
    assert AuditAction.AUTH_LOGIN.value in listed_actions


@pytest.mark.asyncio
async def test_audit_filter_by_action(
    auth_client: tuple[AsyncClient, dict[str, Any]],
) -> None:
    client, _ = auth_client
    res = await client.get("/api/v1/audit-logs", params={"action": AuditAction.AUTH_LOGIN.value})
    assert res.status_code == 200
    items = res.json()["data"]["items"]
    assert items
    assert all(item["action"] == AuditAction.AUTH_LOGIN.value for item in items)


@pytest.mark.asyncio
async def test_audit_requires_scope(
    async_client: AsyncClient,
    admin_db_session: AsyncSession,
) -> None:
    """Member without audit:read must receive 403."""
    uid = str(uuid.uuid4())[:8]
    email = f"member-{uid}@nidus.com"
    password = "TestPassword123!"

    onboard = await async_client.post(
        "/api/v1/organizations/onboarding",
        json={
            "organization_name": f"Audit Scope Org {uid}",
            "organization_slug": f"audit-scope-{uid}",
            "admin_email": f"owner-{uid}@nidus.com",
            "password": password,
        },
    )
    assert onboard.status_code == 201
    org_id = onboard.json()["data"]["organization_id"]

    login = await async_client.post(
        "/api/v1/auth/login",
        data={"username": f"owner-{uid}@nidus.com", "password": password},
    )
    owner_token = login.json()["data"]["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {owner_token}"})

    roles_res = await async_client.get("/api/v1/identity/roles")
    assert roles_res.status_code == 200
    member_role = next(r for r in roles_res.json()["data"] if r["name"] == "Member")

    invite_res = await async_client.post(
        "/api/v1/identity/invitations",
        json={"email": email, "role_id": member_role["id"]},
    )
    assert invite_res.status_code == 201

    # Load invite token via admin (not exposed in create response)
    from app.models.identity.invitation import Invitation

    invite = (
        await admin_db_session.execute(
            select(Invitation).where(Invitation.email == email, Invitation.organization_id == uuid.UUID(org_id))
        )
    ).scalar_one()

    async_client.headers.pop("Authorization", None)
    accept = await async_client.post(
        "/api/v1/identity/invitations/accept",
        json={"token": invite.token, "password": password},
    )
    assert accept.status_code == 200

    member_login = await async_client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert member_login.status_code == 200
    member_body = member_login.json()["data"]
    if member_body.get("org_selection_required"):
        select_res = await async_client.post(
            "/api/v1/auth/select-org",
            json={"pre_auth_token": member_body["pre_auth_token"], "organization_id": org_id},
        )
        assert select_res.status_code == 200
        member_token = select_res.json()["data"]["access_token"]
    else:
        member_token = member_body["access_token"]

    async_client.headers.update({"Authorization": f"Bearer {member_token}"})
    denied = await async_client.get("/api/v1/audit-logs")
    assert denied.status_code == 403
    assert denied.json()["code"] in {"MISSING_SCOPE", "NO_ACTIVE_ROLE", "FORBIDDEN"} or denied.json().get(
        "status"
    ) == "error"


@pytest.mark.asyncio
async def test_audit_rls_isolation(db_session: AsyncSession, admin_db_session: AsyncSession) -> None:
    org_a = uuid.uuid4()
    org_b = uuid.uuid4()

    async with admin_db_session.begin():
        await admin_db_session.execute(
            text(
                """
                INSERT INTO organization (id, name, slug, is_active, created_at, updated_at)
                VALUES
                  (:a, 'Audit A', :sa, true, now(), now()),
                  (:b, 'Audit B', :sb, true, now(), now())
                """
            ),
            {"a": org_a, "b": org_b, "sa": f"audit-a-{org_a}", "sb": f"audit-b-{org_b}"},
        )
        await admin_db_session.execute(
            text(
                """
                INSERT INTO audit_log (id, organization_id, action, metadata, created_at)
                VALUES
                  (:id_a, :a, 'organization.create', '{}'::jsonb, now()),
                  (:id_b, :b, 'organization.create', '{}'::jsonb, now())
                """
            ),
            {"id_a": uuid.uuid4(), "id_b": uuid.uuid4(), "a": org_a, "b": org_b},
        )

    async with db_session.begin():
        await db_session.execute(text(f"SET LOCAL app.current_organization_id = '{org_a}'"))
        rows = (await db_session.execute(select(AuditLog))).scalars().all()
        assert len(rows) == 1
        assert rows[0].organization_id == org_a

    async with db_session.begin():
        await db_session.execute(text(f"SET LOCAL app.current_organization_id = '{org_b}'"))
        rows = (await db_session.execute(select(AuditLog))).scalars().all()
        assert len(rows) == 1
        assert rows[0].organization_id == org_b


@pytest.mark.asyncio
async def test_role_create_emits_audit(auth_client: tuple[AsyncClient, dict[str, Any]]) -> None:
    client, _ = auth_client
    res = await client.post(
        "/api/v1/identity/roles",
        json={
            "name": "Auditor Helper",
            "description": "temp",
            "scopes": [NidusScope.ORG_READ.value, NidusScope.AUDIT_READ.value],
        },
    )
    assert res.status_code == 201
    role_id = res.json()["data"]["id"]

    logs = await client.get("/api/v1/audit-logs", params={"action": AuditAction.ROLE_CREATE.value})
    assert logs.status_code == 200
    items = logs.json()["data"]["items"]
    assert any(item["resource_id"] == role_id for item in items)
