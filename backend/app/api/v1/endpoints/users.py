from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ScopeGuard, get_current_tenant_session, get_jwt_payload, get_language
from app.core.db import get_session
from app.core.i18n.service import i18n
from app.core.rate_limit import RateLimit
from app.models.identity.scopes import NidusScope
from app.schemas.requests.user import UpdateProfileRequest
from app.schemas.responses.auth import UserOrganizationSummary
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.user import UserProfileResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me/organizations", response_model=GenericResponse[list[UserOrganizationSummary]])
async def list_my_organizations(
    session: AsyncSession = Depends(get_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
) -> GenericResponse[list[UserOrganizationSummary]]:
    user_id = UUID(str(payload["sub"]))
    organizations = await AuthService.list_user_organizations(session, user_id)
    return GenericResponse(data=organizations)


@router.get("/me", response_model=GenericResponse[UserProfileResponse], dependencies=[Depends(ScopeGuard(NidusScope.ORG_READ))])
async def get_my_profile(
    session: AsyncSession = Depends(get_current_tenant_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
) -> GenericResponse[UserProfileResponse]:
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
    user_id = UUID(str(payload["sub"]))

    await UserService.update_profile(session, user_id, data)

    success_msg = i18n.t("success.profile_updated", lang=lang)
    return GenericResponse[Any](data=None, message=success_msg)


@router.post(
    "/me/avatar",
    response_model=GenericResponse[dict[str, str]],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimit("users.avatar", tier="moderate"))],
)
async def upload_my_avatar(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_current_tenant_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
    lang: str = Depends(get_language),
) -> GenericResponse[dict[str, str]]:
    user_id = UUID(str(payload["sub"]))
    url = await UserService.set_avatar(session, user_id, file)
    return GenericResponse(
        data={"avatar_url": url},
        message=i18n.t("success.avatar_updated", lang=lang),
    )


@router.delete(
    "/me/avatar",
    response_model=GenericResponse[Any],
    status_code=status.HTTP_200_OK,
)
async def delete_my_avatar(
    session: AsyncSession = Depends(get_current_tenant_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
    lang: str = Depends(get_language),
) -> GenericResponse[Any]:
    user_id = UUID(str(payload["sub"]))
    await UserService.clear_avatar(session, user_id)
    return GenericResponse[Any](data=None, message=i18n.t("success.avatar_removed", lang=lang))
