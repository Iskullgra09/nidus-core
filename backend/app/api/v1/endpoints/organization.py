from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import ScopeGuard, get_current_tenant_session, get_jwt_payload, get_language
from app.core.db import get_session
from app.core.i18n.service import i18n
from app.models import Member
from app.models.identity.scopes import NidusScope
from app.schemas.requests.organization import OnboardingCreate
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.identity import UserProfileResponse
from app.schemas.responses.organization import OnBoardingResponse
from app.services.organization_service import OrganizationService

router = APIRouter()


@router.post(
    "/onboarding",
    response_model=GenericResponse[OnBoardingResponse],
    status_code=status.HTTP_201_CREATED,
)
async def onboard_tenant(data: OnboardingCreate, session: AsyncSession = Depends(get_session), lang: str = Depends(get_language)):
    """Creates a new organization, its first admin user, and assigns the correct roles."""
    org_id, user_id = await OrganizationService.create_onboarding(session, data)

    response_data = OnBoardingResponse(
        organization_id=org_id,
        user_id=user_id,
    )

    success_msg = i18n.t("success.onboarding_complete", lang=lang)

    return GenericResponse(data=response_data, message=success_msg)


@router.get("/me", response_model=GenericResponse[UserProfileResponse], dependencies=[Depends(ScopeGuard(NidusScope.ORG_READ))])
async def get_my_profile(
    session: AsyncSession = Depends(get_current_tenant_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
):
    """
    Returns the complete profile for the currently authenticated user,
    including their identity, role, scopes, and organization details.
    """

    user_id = UUID(str(payload["sub"]))
    MemberModel = cast(Any, Member)

    stmt = (
        select(Member)
        .where(MemberModel.user_id == user_id, MemberModel.deleted_at.is_(None))
        .options(selectinload(MemberModel.user), selectinload(MemberModel.role), selectinload(MemberModel.organization))
    )
    result = await session.execute(stmt)
    member = result.scalar_one()

    m = cast(Any, member)

    profile_data = UserProfileResponse(
        id=m.user.id,
        email=m.user.email,
        is_superuser=m.user.is_superuser,
        role_name=m.role.name,
        scopes=m.role.scopes,
        organization=m.organization,
    )

    return GenericResponse(data=profile_data)
