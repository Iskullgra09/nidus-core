from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ScopeGuard, get_current_tenant_session, get_jwt_payload, get_language
from app.api.pagination import CursorParams
from app.core.db import get_session
from app.core.exceptions.base import AuthenticationError, ConflictError, EntityNotFoundError
from app.core.i18n.service import i18n
from app.models.identity.invitation import Invitation
from app.models.identity.scopes import NidusScope
from app.schemas.filters.identity import MemberFilter
from app.schemas.requests.identity import InvitationAccept, InvitationCreate, MemberUpdateRole
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.identity import InvitationAcceptedResponse, InvitationResponse, MemberResponse, RoleResponse
from app.schemas.responses.pagination import CursorPage
from app.services.email_service import EmailService
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
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_current_tenant_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
    lang: str = Depends(get_language),
):
    raw_org_id = payload.get("org_id")
    if not raw_org_id:
        raise AuthenticationError(message_key="common.forbidden")

    org_id = UUID(str(raw_org_id))
    invite = await IdentityService.invite_user(session, org_id=org_id, email=data.email, role_id=data.role_id)
    background_tasks.add_task(EmailService.send_invitation_email, email=invite.email, token=invite.token, lang=lang)

    return GenericResponse(data=invite, message=i18n.t("success.invitation_sent", lang=lang))


@router.get("/invitations/verify/{token}", response_model=GenericResponse[dict[str, bool]], status_code=status.HTTP_200_OK)
async def verify_invitation(token: str, session: AsyncSession = Depends(get_session), lang: str = Depends(get_language)):
    """Public Endpoint: Verifies if a token is valid before showing the accept form."""
    await session.execute(text("SET LOCAL app.current_organization_id = ''"))

    InvitationModel = cast(Any, Invitation)

    stmt = select(Invitation).where(InvitationModel.token == token, InvitationModel.deleted_at.is_(None))

    invitation = (await session.execute(stmt)).scalar_one_or_none()

    if not invitation:
        raise EntityNotFoundError(entity="invitation")

    if invitation.is_accepted:
        raise ConflictError(message_key="invitation.already_accepted")

    if invitation.expires_at < datetime.now(timezone.utc):
        raise ConflictError(message_key="invitation.expired")

    return GenericResponse(data={"valid": True}, message=i18n.t("success.valid_token", lang=lang))


@router.post("/invitations/accept", response_model=GenericResponse[InvitationAcceptedResponse], status_code=status.HTTP_200_OK)
async def accept_invitation(
    data: InvitationAccept,
    session: AsyncSession = Depends(get_session),
    lang: str = Depends(get_language),
):
    user_id, org_id, role_id = await IdentityService.accept_invitation(session=session, token=data.token, password=data.password)
    response_data = InvitationAcceptedResponse(user_id=user_id, organization_id=org_id, role_id=role_id)

    return GenericResponse(data=response_data, message=i18n.t("success.invitation_accepted", lang=lang))


@router.get(
    "/members",
    response_model=GenericResponse[CursorPage[MemberResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeGuard(NidusScope.ORG_READ))],
)
async def list_members(
    pagination: CursorParams = Depends(),
    filters: MemberFilter = Depends(),
    session: AsyncSession = Depends(get_current_tenant_session),
    lang: str = Depends(get_language),
):
    page_data = await IdentityService.get_organization_members(session, pagination, filters)
    return GenericResponse(data=page_data, message=i18n.t("success.members_retrieved", lang=lang))


@router.patch(
    "/members/{member_id}/role",
    response_model=GenericResponse[MemberResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeGuard(NidusScope.MEMBER_WRITE))],
)
async def update_member_role(
    member_id: UUID,
    data: MemberUpdateRole,
    session: AsyncSession = Depends(get_current_tenant_session),
    lang: str = Depends(get_language),
):
    member = await IdentityService.update_member_role(session, member_id, data.role_id)
    return GenericResponse(data=member, message=i18n.t("success.member_updated", lang=lang))


@router.delete(
    "/members/{member_id}",
    response_model=GenericResponse[Any],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeGuard(NidusScope.MEMBER_WRITE))],
)
async def remove_member(
    member_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    lang: str = Depends(get_language),
):
    await IdentityService.remove_member(session, member_id)

    success_msg = i18n.t("success.member_removed", lang=lang)

    return GenericResponse[Any](data=None, message=success_msg)


@router.get(
    "/roles",
    response_model=GenericResponse[list[RoleResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeGuard(NidusScope.ROLE_READ))],
)
async def list_roles(
    session: AsyncSession = Depends(get_current_tenant_session),
    lang: str = Depends(get_language),
):
    roles = await IdentityService.get_roles(session)
    return GenericResponse(data=roles, message=i18n.t("success.roles_retrieved", lang=lang))
