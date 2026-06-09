from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ScopeGuard, get_current_tenant_session, get_jwt_payload, get_language
from app.api.pagination import CursorParams
from app.core.db import get_session
from app.core.exceptions.base import AuthenticationError, ConflictError, EntityNotFoundError
from app.core.i18n.service import i18n
from app.core.rls import clear_rls_context
from app.models.identity.invitation import Invitation
from app.models.identity.scopes import NidusScope
from app.schemas.filters.identity import InvitationFilter, MemberFilter
from app.schemas.requests.identity import (
    InvitationAccept,
    InvitationCreate,
    MemberUpdateRole,
    RoleCreate,
    RoleUpdate,
)
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.identity import (
    InvitationAcceptedResponse,
    InvitationResponse,
    MemberResponse,
    RoleResponse,
    ScopeResponse,
)
from app.schemas.responses.pagination import CursorPage
from app.services.email_service import EmailService
from app.services.identity_service import IdentityService

router = APIRouter()


@router.post(
    "/invitations",
    response_model=GenericResponse[InvitationResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ScopeGuard(NidusScope.MEMBER_INVITE))],
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
    await clear_rls_context(session)

    InvitationModel = cast(Any, Invitation)

    stmt = select(Invitation).where(InvitationModel.token == token, InvitationModel.deleted_at.is_(None))

    invitation = (await session.execute(stmt)).scalar_one_or_none()

    if not invitation:
        raise EntityNotFoundError(entity="invitation")

    if invitation.deleted_at is not None:
        raise ConflictError(message_key="invitation.revoked")

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
    "/invitations",
    response_model=GenericResponse[list[InvitationResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeGuard(NidusScope.MEMBER_READ))],
)
async def list_invitations(
    filters: InvitationFilter = Depends(),
    session: AsyncSession = Depends(get_current_tenant_session),
    lang: str = Depends(get_language),
):
    invitations = await IdentityService.list_invitations(session, filters)
    return GenericResponse(data=invitations, message=i18n.t("success.invitations_retrieved", lang=lang))


@router.delete(
    "/invitations/{invitation_id}",
    response_model=GenericResponse[Any],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeGuard(NidusScope.MEMBER_INVITE))],
)
async def revoke_invitation(
    invitation_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    lang: str = Depends(get_language),
):
    await IdentityService.revoke_invitation(session, invitation_id)
    return GenericResponse(data=None, message=i18n.t("success.invitation_revoked", lang=lang))


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


@router.post(
    "/roles",
    response_model=GenericResponse[RoleResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ScopeGuard(NidusScope.ROLE_WRITE))],
)
async def create_role(
    data: RoleCreate,
    session: AsyncSession = Depends(get_current_tenant_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
    lang: str = Depends(get_language),
):
    raw_org_id = payload.get("org_id")
    if not raw_org_id:
        raise AuthenticationError(message_key="common.forbidden")

    role = await IdentityService.create_role(session, org_id=UUID(str(raw_org_id)), data=data)
    return GenericResponse(data=role, message=i18n.t("success.role_created", lang=lang))


@router.patch(
    "/roles/{role_id}",
    response_model=GenericResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeGuard(NidusScope.ROLE_WRITE))],
)
async def update_role(
    role_id: UUID,
    data: RoleUpdate,
    session: AsyncSession = Depends(get_current_tenant_session),
    lang: str = Depends(get_language),
):
    role = await IdentityService.update_role(session, role_id, data)
    return GenericResponse(data=role, message=i18n.t("success.role_updated", lang=lang))


@router.delete(
    "/roles/{role_id}",
    response_model=GenericResponse[Any],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeGuard(NidusScope.ROLE_WRITE))],
)
async def delete_role(
    role_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    lang: str = Depends(get_language),
):
    await IdentityService.delete_role(session, role_id)
    return GenericResponse(data=None, message=i18n.t("success.role_deleted", lang=lang))


@router.get(
    "/scopes",
    response_model=GenericResponse[list[ScopeResponse]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeGuard(NidusScope.ROLE_READ))],
)
async def list_scopes(lang: str = Depends(get_language)):
    scopes = [
        ScopeResponse(value=scope.value, group=NidusScope.scope_group(scope.value))
        for scope in NidusScope
        if scope != NidusScope.SUPERADMIN
    ]
    return GenericResponse(data=scopes, message=i18n.t("success.scopes_retrieved", lang=lang))
