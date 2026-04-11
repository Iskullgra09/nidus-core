from typing import Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ScopeGuard, get_current_tenant_session, get_jwt_payload, get_language
from app.api.pagination import CursorParams
from app.core.db import get_session
from app.core.exceptions.base import AuthenticationError
from app.core.i18n.service import i18n
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
    """Invites a new member to the organization."""
    raw_org_id = payload.get("org_id")
    if not raw_org_id:
        raise AuthenticationError(message_key="common.forbidden")

    org_id = UUID(str(raw_org_id))

    invite = await IdentityService.invite_user(session, org_id=org_id, email=data.email, role_id=data.role_id)

    background_tasks.add_task(EmailService.send_invitation_email, email=invite.email, token=invite.token, lang=lang)

    success_msg = i18n.t("success.invitation_sent", lang=lang)
    return GenericResponse(data=invite, message=success_msg)


@router.post("/invitations/accept", response_model=GenericResponse[InvitationAcceptedResponse], status_code=status.HTTP_200_OK)
async def accept_invitation(
    data: InvitationAccept,
    session: AsyncSession = Depends(get_session),
    lang: str = Depends(get_language),
):
    """Public endpoint. Consumes an invitation token and registers the user."""
    user_id, org_id, role_id = await IdentityService.accept_invitation(session=session, token=data.token, password=data.password)

    success_msg = i18n.t("success.invitation_accepted", lang=lang)
    response_data = InvitationAcceptedResponse(user_id=user_id, organization_id=org_id, role_id=role_id)

    return GenericResponse(data=response_data, message=success_msg)


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
    """Retrieves a paginated and filtered list of organization members."""
    page_data = await IdentityService.get_organization_members(session, pagination, filters)

    success_msg = i18n.t("success.members_retrieved", lang=lang)
    return GenericResponse(data=page_data, message=success_msg)


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
    """Updates a member's role within the organization."""
    member = await IdentityService.update_member_role(session, member_id, data.role_id)

    success_msg = i18n.t("success.member_updated", lang=lang)
    return GenericResponse(data=member, message=success_msg)


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
) -> GenericResponse[Any]:
    """Removes (soft-deletes) a member from the organization."""
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
    """Retrieves all roles defined for the current organization."""
    roles = await IdentityService.get_roles(session)

    success_msg = i18n.t("success.roles_retrieved", lang=lang)
    return GenericResponse(data=roles, message=success_msg)
