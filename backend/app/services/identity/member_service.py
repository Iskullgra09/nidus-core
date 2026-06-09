from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.base import EntityNotFoundError
from app.core.pagination import paginate_with_cursor
from app.models import Member, User
from app.models.identity.role import Role
from app.schemas.filters.identity import MemberFilter
from app.schemas.requests.pagination import CursorParams
from app.schemas.responses.pagination import CursorPage, PageInfo


class MemberService:
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
            session=session,
            stmt=stmt,
            model_class=MemberModel,
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return CursorPage(items=list(items), page_info=PageInfo(has_next_page=has_next, end_cursor=end_cursor))

    @staticmethod
    async def update_member_role(session: AsyncSession, member_id: UUID, new_role_id: UUID) -> Member:
        MemberModel = cast(Any, Member)

        stmt = select(Member).where(MemberModel.id == member_id, MemberModel.deleted_at.is_(None))
        member = (await session.execute(stmt)).scalar_one_or_none()

        if not member:
            raise EntityNotFoundError(entity="member")

        member.role_id = new_role_id
        await session.commit()

        fresh_stmt = (
            select(Member)
            .where(MemberModel.id == member_id)
            .options(selectinload(MemberModel.user), selectinload(MemberModel.role))
        )
        return (await session.execute(fresh_stmt)).scalar_one()

    @staticmethod
    async def remove_member(session: AsyncSession, member_id: UUID) -> None:
        MemberModel = cast(Any, Member)

        stmt = select(Member).where(MemberModel.id == member_id, MemberModel.deleted_at.is_(None))
        member = (await session.execute(stmt)).scalar_one_or_none()

        if not member:
            raise EntityNotFoundError(entity="member")

        member.deleted_at = datetime.now(timezone.utc)
        await session.commit()
