from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.pagination import CursorParams
from app.core.exceptions.base import AuthenticationError, ConflictError, EntityNotFoundError
from app.core.pagination import paginate_with_cursor
from app.core.security import hash_password, verify_password
from app.models import Member, User
from app.models.identity.invitation import Invitation
from app.schemas.responses.pagination import CursorPage, PageInfo


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
            raise ConflictError(message_key="invitation.already_pending", email=email)

        new_invite = Invitation(email=email, role_id=role_id, organization_id=org_id)
        session.add(new_invite)
        await session.commit()
        await session.refresh(new_invite)
        return new_invite

    @staticmethod
    async def get_organization_members(session: AsyncSession, pagination: CursorParams) -> CursorPage[Member]:
        """
        Lists all members of the current organization using cursor pagination.
        Thanks to selectinload/Relationship, we get the email and role name easily.
        """
        MemberModel = cast(Any, Member)

        stmt = (
            select(Member).where(MemberModel.deleted_at.is_(None)).options(selectinload(MemberModel.user), selectinload(MemberModel.role))
        )

        items, end_cursor, has_next = await paginate_with_cursor(
            session=session, stmt=stmt, model_class=MemberModel, limit=pagination.limit, cursor=pagination.cursor
        )

        return CursorPage(items=list(items), page_info=PageInfo(has_next_page=has_next, end_cursor=end_cursor))

    @staticmethod
    async def accept_invitation(session: AsyncSession, token: str, password: str) -> tuple[UUID, UUID, UUID]:
        """
        Validates the token, creates/links the User, and creates the Member.
        This function bypasses RLS because the user is not authenticated yet.
        """
        await session.execute(text("SET LOCAL app.current_organization_id = ''"))
        await session.execute(text("SET LOCAL app.current_user_id = ''"))

        InvitationModel = cast(Any, Invitation)
        UserModel = cast(Any, User)

        stmt = select(Invitation).where(InvitationModel.token == token, InvitationModel.deleted_at.is_(None))
        result = await session.execute(stmt)
        invitation = result.scalar_one_or_none()

        if not invitation:
            raise EntityNotFoundError(entity="invitation")

        if invitation.is_accepted:
            raise ConflictError(message_key="invitation.already_accepted")

        if invitation.expires_at < datetime.now(timezone.utc):
            raise ConflictError(message_key="invitation.expired")

        user_stmt = select(User).where(UserModel.email == invitation.email)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            user = User(email=invitation.email, hashed_password=hash_password(password), is_active=True)
            session.add(user)
            await session.flush()
        else:
            if not verify_password(password, user.hashed_password):
                raise AuthenticationError(message_key="invitation.existing_user_wrong_password")

            member_stmt = select(Member).where(
                cast(Any, Member).user_id == user.id,
                cast(Any, Member).organization_id == invitation.organization_id,
                cast(Any, Member).deleted_at.is_(None),
            )
            existing_member = (await session.execute(member_stmt)).scalar_one_or_none()

            if existing_member:
                raise ConflictError(message_key="onboarding.user_already_in_org")

        new_member = Member(user_id=user.id, organization_id=invitation.organization_id, role_id=invitation.role_id)
        session.add(new_member)

        invitation.is_accepted = True

        await session.commit()
        return user.id, invitation.organization_id, invitation.role_id
