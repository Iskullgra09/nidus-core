from typing import Any, Dict, Optional, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import paginate_with_cursor
from app.core.request_context import RequestContext
from app.models.audit import AuditAction, AuditLog, AuditResourceType
from app.schemas.filters.audit import AuditLogFilter
from app.schemas.requests.pagination import CursorParams
from app.schemas.responses.audit import AuditLogResponse
from app.schemas.responses.pagination import CursorPage, PageInfo


class AuditService:
    """Central append-only audit writer + tenant-scoped reader."""

    @staticmethod
    async def record(
        session: AsyncSession,
        *,
        action: AuditAction | str,
        organization_id: Optional[UUID] = None,
        actor_user_id: Optional[UUID] = None,
        resource_type: Optional[AuditResourceType | str] = None,
        resource_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        commit: bool = False,
    ) -> AuditLog:
        """
        Inserts one audit row. Callers that already commit should leave commit=False
        so the row shares their transaction. Auth flows that don't mutate other rows
        may pass commit=True.
        """
        org_id = organization_id or RequestContext.get_organization()
        if org_id is None:
            raise ValueError("organization_id is required to record an audit event")

        entry = AuditLog(
            organization_id=org_id,
            actor_user_id=actor_user_id if actor_user_id is not None else RequestContext.get_actor(),
            action=str(action),
            resource_type=str(resource_type) if resource_type is not None else None,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address if ip_address is not None else RequestContext.get_client_ip(),
        )
        session.add(entry)
        await session.flush()

        if commit:
            await session.commit()

        return entry

    @staticmethod
    async def list_logs(
        session: AsyncSession,
        pagination: CursorParams,
        filters: AuditLogFilter,
    ) -> CursorPage[AuditLogResponse]:
        AuditModel = cast(Any, AuditLog)
        stmt = select(AuditLog)

        if filters.action:
            stmt = stmt.where(AuditModel.action == filters.action)

        if filters.actor_user_id:
            stmt = stmt.where(AuditModel.actor_user_id == filters.actor_user_id)

        if filters.resource_type:
            stmt = stmt.where(AuditModel.resource_type == filters.resource_type)

        items, end_cursor, has_next = await paginate_with_cursor(
            session=session,
            stmt=stmt,
            model_class=AuditModel,
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return CursorPage(
            items=[
                AuditLogResponse(
                    id=row.id,
                    organization_id=row.organization_id,
                    actor_user_id=row.actor_user_id,
                    action=row.action,
                    resource_type=row.resource_type,
                    resource_id=row.resource_id,
                    metadata=row.details,
                    ip_address=row.ip_address,
                    created_at=row.created_at,
                )
                for row in items
            ],
            page_info=PageInfo(has_next_page=has_next, end_cursor=end_cursor),
        )
