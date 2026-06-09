import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlmodel import col

from app.models.identity.member import Member
from app.models.identity.role import Role
from app.models.identity.scopes import DefaultRole


@pytest.mark.asyncio
async def test_accept_invitation_creates_member(async_client: AsyncClient, auth_client, db_session) -> None:
    client, context = auth_client
    org_id = context["org_id"]

    async with db_session.begin():
        await db_session.execute(text(f"SET LOCAL app.current_organization_id = '{org_id}'"))
        member_role = (
            await db_session.execute(
                select(Role).where(col(Role.name) == DefaultRole.MEMBER.value, col(Role.organization_id) == uuid.UUID(org_id))
            )
        ).scalar_one()

    invite_email = f"invited-{uuid.uuid4().hex[:8]}@nidus.com"
    invite_res = await client.post(
        "/api/v1/identity/invitations",
        json={"email": invite_email, "role_id": str(member_role.id)},
    )
    assert invite_res.status_code == 201

    async with db_session.begin():
        await db_session.execute(text(f"SET LOCAL app.current_organization_id = '{org_id}'"))
        from app.models.identity.invitation import Invitation

        invitation = (
            await db_session.execute(select(Invitation).where(col(Invitation.email) == invite_email))
        ).scalar_one()
        invite_token = invitation.token

    verify_res = await async_client.get(f"/api/v1/identity/invitations/verify/{invite_token}")
    assert verify_res.status_code == 200
    assert verify_res.json()["data"]["valid"] is True

    accept_res = await async_client.post(
        "/api/v1/identity/invitations/accept",
        json={"token": invite_token, "password": "InvitePass123!"},
    )
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "success"

    async with db_session.begin():
        await db_session.execute(text("SET LOCAL app.current_organization_id = ''"))
        member = (
            await db_session.execute(
                select(Member).where(
                    col(Member.organization_id) == uuid.UUID(org_id),
                    col(Member.deleted_at).is_(None),
                )
            )
        ).scalars().all()
        assert len(member) == 2
