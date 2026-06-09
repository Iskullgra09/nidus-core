from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ScopeGuard, get_current_tenant_session, get_jwt_payload, get_language
from app.core.i18n.service import i18n
from app.models.identity.scopes import NidusScope
from app.schemas.requests.user import UpdateProfileRequest
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.user import UserProfileResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=GenericResponse[UserProfileResponse], dependencies=[Depends(ScopeGuard(NidusScope.ORG_READ))])
async def get_my_profile(
    session: AsyncSession = Depends(get_current_tenant_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
) -> GenericResponse[UserProfileResponse]:
    """Returns the complete profile and context for the authenticated user."""
    user_id = UUID(str(payload["sub"]))
    profile_data = await UserService.get_my_profile(session, user_id)
    return GenericResponse(data=profile_data)


@router.put("/me", response_model=GenericResponse[Any], status_code=status.HTTP_200_OK)
async def update_my_profile(
    data: UpdateProfileRequest,
    session: AsyncSession = Depends(get_current_tenant_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
    lang: str = Depends(get_language),
) -> GenericResponse[Any]:
    """Updates the authenticated user's personal profile and preferences."""
    user_id = UUID(str(payload["sub"]))

    await UserService.update_profile(session, user_id, data)

    success_msg = i18n.t("success.profile_updated", lang=lang)
    return GenericResponse[Any](data=None, message=success_msg)
