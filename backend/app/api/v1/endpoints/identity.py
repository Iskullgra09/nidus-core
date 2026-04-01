from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ScopeGuard, get_current_tenant_session, get_jwt_payload, get_language
from app.core.db import get_session
from app.core.exceptions.base import AuthenticationError
from app.core.i18n.service import i18n
from app.models.identity.scopes import NidusScope
from app.schemas.requests.identity import InvitationAccept, InvitationCreate
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.identity import InvitationAcceptedResponse, InvitationResponse
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
    lang: str = Depends(get_language),
):
    """
    Invites a new member to the organization.
    """
    raw_org_id = payload.get("org_id")
    if not raw_org_id:
        raise AuthenticationError(message_key="common.forbidden")

    org_id = UUID(str(raw_org_id))

    invite = await IdentityService.invite_user(session, org_id=org_id, email=data.email, role_id=data.role_id)

    success_msg = i18n.t("success.invitation_sent", lang=lang)
    return GenericResponse(data=invite, message=success_msg)


@router.post("/invitations/accept", response_model=GenericResponse[InvitationAcceptedResponse], status_code=status.HTTP_200_OK)
async def accept_invitation(
    data: InvitationAccept,
    session: AsyncSession = Depends(get_session),
    lang: str = Depends(get_language),
):
    """
    Public endpoint. Consumes an invitation token and registers the user.
    """
    user_id, org_id, role_id = await IdentityService.accept_invitation(session=session, token=data.token, password=data.password)

    success_msg = i18n.t("success.invitation_accepted", lang=lang)

    response_data = InvitationAcceptedResponse(user_id=user_id, organization_id=org_id, role_id=role_id)

    return GenericResponse(data=response_data, message=success_msg)
