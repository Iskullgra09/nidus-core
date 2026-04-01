from typing import Any, List, cast
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity.invitation import Invitation
from app.models.identity.member import Member


class IdentityService:
    @staticmethod
    async def invite_user(session: AsyncSession, org_id: UUID, email: str, role_id: UUID) -> Invitation:
        """
        Creates a pending invitation. RLS ensures we only create it for our org.
        """
        InvitationModel = cast(Any, Invitation)

        stmt = select(Invitation).where(
            InvitationModel.email == email,
            InvitationModel.organization_id == org_id,
            InvitationModel.is_accepted.is_(False),
            InvitationModel.deleted_at.is_(None),
        )
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An invitation is already pending for this email.")

        new_invite = Invitation(email=email, role_id=role_id, organization_id=org_id)
        session.add(new_invite)
        await session.commit()
        await session.refresh(new_invite)
        return new_invite

    @staticmethod
    async def get_organization_members(session: AsyncSession) -> List[Member]:
        """
        Lists all members of the current organization.
        Thanks to selectinload/Relationship, we get the email and role name easily.
        """
        stmt = select(Member).where(cast(Any, Member).deleted_at.is_(None))
        result = await session.execute(stmt)
        return list(result.scalars().all())
