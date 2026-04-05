from datetime import datetime, timezone
from typing import Any, Tuple, cast
from uuid import UUID

from sqlalchemy import Select, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.pagination import CursorParams
from app.core.exceptions.base import AuthenticationError, ConflictError, EntityNotFoundError
from app.core.pagination import paginate_with_cursor
from app.core.security import hash_password, verify_password
from app.models import Member, User
from app.models.identity.invitation import Invitation
from app.models.identity.role import Role
from app.schemas.filters.identity import MemberFilter
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
    async def get_organization_members(
        session: AsyncSession,
        pagination: CursorParams,
        filters: MemberFilter,
    ) -> CursorPage[Member]:
        MemberModel = cast(Any, Member)
        RoleModel = cast(Any, Role)
        UserModel = cast(Any, User)

        stmt: Select[Tuple[Member]] = select(Member).join(MemberModel.user).join(MemberModel.role).where(MemberModel.deleted_at.is_(None))

        if filters.email__contains:
            stmt = stmt.where(UserModel.email.ilike(f"%{filters.email__contains}%"))

        if filters.role_name:
            stmt = stmt.where(RoleModel.name == filters.role_name)

        stmt = stmt.options(selectinload(MemberModel.user), selectinload(MemberModel.role))

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
        MemberModel = cast(Any, Member)

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
                MemberModel.user_id == user.id,
                MemberModel.organization_id == invitation.organization_id,
                MemberModel.deleted_at.is_(None),
            )
            existing_member = (await session.execute(member_stmt)).scalar_one_or_none()

            if existing_member:
                raise ConflictError(message_key="onboarding.user_already_in_org")

        new_member = Member(user_id=user.id, organization_id=invitation.organization_id, role_id=invitation.role_id)
        session.add(new_member)

        invitation.is_accepted = True

        await session.commit()
        return user.id, invitation.organization_id, invitation.role_id

    @staticmethod
    async def update_member_role(session: AsyncSession, member_id: UUID, new_role_id: UUID) -> Member:
        """
        Updates the role of an existing member.
        RLS automatically ensures the member belongs to the current organization.
        """
        MemberModel = cast(Any, Member)

        stmt = select(Member).where(MemberModel.id == member_id, MemberModel.deleted_at.is_(None))
        result = await session.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            raise EntityNotFoundError(entity="member")

        member.role_id = new_role_id
        await session.commit()

        fresh_stmt = (
            select(Member).where(MemberModel.id == member_id).options(selectinload(MemberModel.user), selectinload(MemberModel.role))
        )
        fresh_member = (await session.execute(fresh_stmt)).scalar_one()

        return fresh_member

    @staticmethod
    async def remove_member(session: AsyncSession, member_id: UUID) -> None:
        """
        Soft deletes a member from the organization.
        """
        MemberModel = cast(Any, Member)

        stmt = select(Member).where(MemberModel.id == member_id, MemberModel.deleted_at.is_(None))
        result = await session.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            raise EntityNotFoundError(entity="member")

        member.deleted_at = datetime.now(timezone.utc)
        await session.commit()
