from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ScopeGuard, get_current_tenant_session, get_jwt_payload
from app.models.identity.scopes import NidusScope
from app.schemas.requests.identity import InvitationCreate
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.identity import InvitationResponse
from app.services.identity_service import IdentityService

router = APIRouter()


@router.post(
    "/invitations",
    response_model=GenericResponse[InvitationResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ScopeGuard(NidusScope.MEMBER_WRITE))],
)
async def invite_member(
    data: InvitationCreate,
    session: AsyncSession = Depends(get_current_tenant_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
):
    """
    Invites a new member to the organization.
    """
    raw_org_id = payload.get("org_id")
    if not raw_org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contexto de organización no encontrado en el token")

    org_id = UUID(str(raw_org_id))

    invite = await IdentityService.invite_user(session, org_id=org_id, email=data.email, role_id=data.role_id)
    return GenericResponse(data=invite, message="Invitation sent successfully")
