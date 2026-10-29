from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ScopeGuard, get_current_tenant_session, get_language
from app.core.i18n.service import i18n
from app.models.identity.scopes import NidusScope
from app.schemas.filters.audit import AuditLogFilter
from app.schemas.requests.pagination import CursorParams
from app.schemas.responses.audit import AuditLogResponse
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.pagination import CursorPage
from app.services.audit_service import AuditService

router = APIRouter()


@router.get(
    "",
    response_model=GenericResponse[CursorPage[AuditLogResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeGuard(NidusScope.AUDIT_READ))],
)
async def list_audit_logs(
    pagination: CursorParams = Depends(),
    filters: AuditLogFilter = Depends(),
    session: AsyncSession = Depends(get_current_tenant_session),
    lang: str = Depends(get_language),
):
    page = await AuditService.list_logs(session, pagination, filters)
    return GenericResponse(data=page, message=i18n.t("success.audit_logs_retrieved", lang=lang))
