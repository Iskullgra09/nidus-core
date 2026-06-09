from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from sqlalchemy import asc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.pagination import CursorParams
from app.core.exceptions.base import AuthenticationError, ConflictError, EntityNotFoundError
from app.core.pagination import paginate_with_cursor
from app.core.rls import clear_rls_context
from app.core.security import hash_password, verify_password
from app.models import Member, User
from app.models.identity.invitation import Invitation
from app.models.identity.role import Role
from app.models.identity.scopes import DEFAULT_ROLE_NAMES, NidusScope
from app.schemas.filters.identity import InvitationFilter, MemberFilter
from app.schemas.requests.identity import RoleCreate, RoleUpdate
from app.schemas.responses.identity import InvitationResponse, RoleResponse
from app.schemas.responses.pagination import CursorPage, PageInfo


class IdentityService:
    @staticmethod
    def _to_role_response(role: Role) -> RoleResponse:
        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            scopes=role.scopes,
            is_system=role.name in DEFAULT_ROLE_NAMES,
        )

    @staticmethod
    def _validate_custom_role_name(name: str) -> None:
        if name in DEFAULT_ROLE_NAMES:
            raise ConflictError(message_key="role.reserved_name", name=name)

    @staticmethod
    def _validate_scopes(scopes: list[str]) -> None:
        invalid = [scope for scope in scopes if not NidusScope.is_assignable(scope)]
        if invalid:
            raise ConflictError(message_key="role.invalid_scopes", scopes=", ".join(invalid))

    @staticmethod
    def _ensure_custom_role(role: Role | None) -> Role:
        if not role or role.deleted_at is not None:
            raise EntityNotFoundError(entity="role")
        if role.name in DEFAULT_ROLE_NAMES:
            raise ConflictError(message_key="role.system_role_protected")
        return role

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
        await session.flush()
        await session.commit()
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

        stmt = select(Member).join(MemberModel.user).join(MemberModel.role).where(MemberModel.deleted_at.is_(None))

        if filters.email__contains:
            stmt = stmt.where(UserModel.email.ilike(f"%{filters.email__contains}%"))

        if filters.role_name:
            stmt = stmt.where(RoleModel.name == filters.role_name)

        if filters.is_active is not None:
            stmt = stmt.where(UserModel.is_active == filters.is_active)

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
        await clear_rls_context(session)

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

    @staticmethod
    async def get_roles(session: AsyncSession) -> list[RoleResponse]:
        """
        Retrieves all roles available for the current tenant.
        RLS automatically handles the organization filtering.
        """
        RoleModel = cast(Any, Role)
        statement = (
            select(Role)
            .where(RoleModel.deleted_at.is_(None))
            .order_by(asc(Role.name))
        )
        result = await session.execute(statement)
        return [IdentityService._to_role_response(role) for role in result.scalars().all()]

    @staticmethod
    async def create_role(session: AsyncSession, org_id: UUID, data: RoleCreate) -> RoleResponse:
        IdentityService._validate_custom_role_name(data.name)
        IdentityService._validate_scopes(data.scopes)

        RoleModel = cast(Any, Role)
        stmt = select(Role).where(
            RoleModel.name == data.name,
            RoleModel.organization_id == org_id,
            RoleModel.deleted_at.is_(None),
        )
        if (await session.execute(stmt)).scalar_one_or_none():
            raise ConflictError(message_key="role.name_conflict", name=data.name)

        role = Role(
            name=data.name,
            description=data.description,
            scopes=data.scopes,
            organization_id=org_id,
        )
        session.add(role)
        await session.flush()
        await session.commit()
        return IdentityService._to_role_response(role)

    @staticmethod
    async def update_role(session: AsyncSession, role_id: UUID, data: RoleUpdate) -> RoleResponse:
        RoleModel = cast(Any, Role)
        stmt = select(Role).where(RoleModel.id == role_id, RoleModel.deleted_at.is_(None))
        role = IdentityService._ensure_custom_role((await session.execute(stmt)).scalar_one_or_none())

        if data.name is not None and data.name != role.name:
            IdentityService._validate_custom_role_name(data.name)
            duplicate_stmt = select(Role).where(
                RoleModel.name == data.name,
                RoleModel.organization_id == role.organization_id,
                RoleModel.id != role_id,
                RoleModel.deleted_at.is_(None),
            )
            if (await session.execute(duplicate_stmt)).scalar_one_or_none():
                raise ConflictError(message_key="role.name_conflict", name=data.name)
            role.name = data.name

        if data.description is not None:
            role.description = data.description

        if data.scopes is not None:
            IdentityService._validate_scopes(data.scopes)
            role.scopes = data.scopes

        await session.commit()
        return IdentityService._to_role_response(role)

    @staticmethod
    async def delete_role(session: AsyncSession, role_id: UUID) -> None:
        RoleModel = cast(Any, Role)
        MemberModel = cast(Any, Member)

        stmt = select(Role).where(RoleModel.id == role_id, RoleModel.deleted_at.is_(None))
        role = IdentityService._ensure_custom_role((await session.execute(stmt)).scalar_one_or_none())

        member_count_stmt = select(func.count()).select_from(Member).where(
            MemberModel.role_id == role_id,
            MemberModel.deleted_at.is_(None),
        )
        member_count = (await session.execute(member_count_stmt)).scalar_one()
        if member_count > 0:
            raise ConflictError(message_key="role.in_use")

        role.deleted_at = datetime.now(timezone.utc)
        await session.commit()

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
