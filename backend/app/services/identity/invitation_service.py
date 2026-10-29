from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.base import AuthenticationError, ConflictError, EntityNotFoundError
from app.core.rls import clear_rls_context
from app.core.security import hash_password, verify_password
from app.models import Member, User
from app.models.identity.invitation import Invitation
from app.models.identity.role import Role
from app.schemas.filters.identity import InvitationFilter
from app.schemas.responses.identity import InvitationResponse


class InvitationService:
    @staticmethod
    async def get_valid_invitation(session: AsyncSession, token: str) -> Invitation:
        """Loads a pending, non-expired invitation by token (public / cross-tenant flow)."""
        await clear_rls_context(session)

        InvitationModel = cast(Any, Invitation)
        stmt = select(Invitation).where(
            InvitationModel.token == token,
            InvitationModel.deleted_at.is_(None),
        )
        invitation = (await session.execute(stmt)).scalar_one_or_none()

        if not invitation:
            raise EntityNotFoundError(entity="invitation")

        if invitation.is_accepted:
            raise ConflictError(message_key="invitation.already_accepted")

        if invitation.expires_at < datetime.now(timezone.utc):
            raise ConflictError(message_key="invitation.expired")

        return invitation

    @staticmethod
    async def invite_user(session: AsyncSession, org_id: UUID, email: str, role_id: UUID) -> Invitation:
        InvitationModel = cast(Any, Invitation)

        stmt = select(Invitation).where(
            InvitationModel.email == email,
            InvitationModel.organization_id == org_id,
            InvitationModel.is_accepted.is_(False),
            InvitationModel.deleted_at.is_(None),
        )
        if (await session.execute(stmt)).scalar_one_or_none():
            raise ConflictError(message_key="invitation.already_pending", email=email)

        new_invite = Invitation(email=email, role_id=role_id, organization_id=org_id)
        session.add(new_invite)
        await session.flush()
        await session.commit()
        return new_invite

    @staticmethod
    async def accept_invitation(session: AsyncSession, token: str, password: str) -> tuple[UUID, UUID, UUID]:
        invitation = await InvitationService.get_valid_invitation(session, token)

        UserModel = cast(Any, User)
        MemberModel = cast(Any, Member)

        user_stmt = select(User).where(UserModel.email == invitation.email)
        user = (await session.execute(user_stmt)).scalar_one_or_none()

        if not user:
            user = User(email=invitation.email, hashed_password=hash_password(password), is_active=True)
            session.add(user)
            await session.flush()
        else:
            if not verify_password(password, user.hashed_password):
                raise AuthenticationError(message_key="invitation.existing_user_wrong_password")

            member_stmt = select(Member).where(
                MemberModel.user_id == user.id,
                MemberModel.organization_id == invitation.organization_id,
                MemberModel.deleted_at.is_(None),
            )
            if (await session.execute(member_stmt)).scalar_one_or_none():
                raise ConflictError(message_key="onboarding.user_already_in_org")

        session.add(
            Member(
                user_id=user.id,
                organization_id=invitation.organization_id,
                role_id=invitation.role_id,
            )
        )
        invitation.is_accepted = True

        await session.commit()
        return user.id, invitation.organization_id, invitation.role_id

    @staticmethod
    async def list_invitations(
        session: AsyncSession,
        filters: InvitationFilter,
    ) -> list[InvitationResponse]:
        InvitationModel = cast(Any, Invitation)
        RoleModel = cast(Any, Role)

        stmt = (
            select(Invitation, Role.name)
            .join(Role, RoleModel.id == InvitationModel.role_id)
            .where(
                InvitationModel.deleted_at.is_(None),
                RoleModel.deleted_at.is_(None),
            )
        )

        if filters.is_accepted is not None:
            stmt = stmt.where(InvitationModel.is_accepted.is_(filters.is_accepted))

        if filters.email__contains:
            stmt = stmt.where(InvitationModel.email.ilike(f"%{filters.email__contains}%"))

        stmt = stmt.order_by(asc(Invitation.created_at))
        rows = (await session.execute(stmt)).all()

        return [
            InvitationResponse(
                id=invitation.id,
                email=invitation.email,
                role_id=invitation.role_id,
                role_name=role_name,
                expires_at=invitation.expires_at,
                is_accepted=invitation.is_accepted,
            )
            for invitation, role_name in rows
        ]

    @staticmethod
    async def revoke_invitation(session: AsyncSession, invitation_id: UUID) -> None:
        InvitationModel = cast(Any, Invitation)

        stmt = select(Invitation).where(
            InvitationModel.id == invitation_id,
            InvitationModel.deleted_at.is_(None),
        )
        invitation = (await session.execute(stmt)).scalar_one_or_none()

        if not invitation:
            raise EntityNotFoundError(entity="invitation")

        if invitation.is_accepted:
            raise ConflictError(message_key="invitation.already_accepted")

        invitation.deleted_at = datetime.now(timezone.utc)
        await session.commit()
