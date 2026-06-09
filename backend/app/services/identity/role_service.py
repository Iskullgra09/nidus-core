from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from sqlalchemy import asc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.base import ConflictError
from app.models import Member
from app.models.identity.role import Role
from app.schemas.requests.identity import RoleCreate, RoleUpdate
from app.schemas.responses.identity import RoleResponse
from app.services.identity.role_policy import (
    ensure_custom_role,
    to_role_response,
    validate_custom_role_name,
    validate_scopes,
)


class RoleService:
    @staticmethod
    async def get_roles(session: AsyncSession) -> list[RoleResponse]:
        RoleModel = cast(Any, Role)
        statement = select(Role).where(RoleModel.deleted_at.is_(None)).order_by(asc(Role.name))
        result = await session.execute(statement)
        return [to_role_response(role) for role in result.scalars().all()]

    @staticmethod
    async def create_role(session: AsyncSession, org_id: UUID, data: RoleCreate) -> RoleResponse:
        validate_custom_role_name(data.name)
        validate_scopes(data.scopes)

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
        return to_role_response(role)

    @staticmethod
    async def update_role(session: AsyncSession, role_id: UUID, data: RoleUpdate) -> RoleResponse:
        RoleModel = cast(Any, Role)
        stmt = select(Role).where(RoleModel.id == role_id, RoleModel.deleted_at.is_(None))
        role = ensure_custom_role((await session.execute(stmt)).scalar_one_or_none())

        if data.name is not None and data.name != role.name:
            validate_custom_role_name(data.name)
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
            validate_scopes(data.scopes)
            role.scopes = data.scopes

        await session.commit()
        return to_role_response(role)

    @staticmethod
    async def delete_role(session: AsyncSession, role_id: UUID) -> None:
        RoleModel = cast(Any, Role)
        MemberModel = cast(Any, Member)

        stmt = select(Role).where(RoleModel.id == role_id, RoleModel.deleted_at.is_(None))
        role = ensure_custom_role((await session.execute(stmt)).scalar_one_or_none())

        member_count_stmt = select(func.count()).select_from(Member).where(
            MemberModel.role_id == role_id,
            MemberModel.deleted_at.is_(None),
        )
        if (await session.execute(member_count_stmt)).scalar_one() > 0:
            raise ConflictError(message_key="role.in_use")

        role.deleted_at = datetime.now(timezone.utc)
        await session.commit()
