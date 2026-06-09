from typing import Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_jwt_payload, get_language
from app.core.db import get_session
from app.core.i18n.service import i18n
from app.schemas.requests.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    SelectOrganizationRequest,
    SwitchOrganizationRequest,
)
from app.schemas.responses.base import GenericResponse
from app.services.auth_service import AuthService
from app.services.email_service import EmailService

router = APIRouter()


@router.post("/login", response_model=GenericResponse[dict[str, Any]], status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
    lang: str = Depends(get_language),
) -> GenericResponse[dict[str, Any]]:
    """
    OAuth2-compatible login.
    Single org: data contains access_token. Multiple orgs: org list + pre_auth_token.
    """
    result = await AuthService.login(session, email=form_data.username, password=form_data.password)
    return GenericResponse(data=result, message=i18n.t("auth.login_success", lang=lang))


@router.post("/select-org", response_model=GenericResponse[dict[str, str]], status_code=status.HTTP_200_OK)
async def select_organization(
    data: SelectOrganizationRequest,
    session: AsyncSession = Depends(get_session),
    lang: str = Depends(get_language),
) -> GenericResponse[dict[str, str]]:
    """Completes login after the user picks an organization."""
    token = await AuthService.select_organization(session, data.pre_auth_token, data.organization_id)
    success_msg = i18n.t("auth.login_success", lang=lang)
    return GenericResponse(data={"access_token": token, "token_type": "bearer"}, message=success_msg)


@router.post("/switch-org", response_model=GenericResponse[dict[str, str]], status_code=status.HTTP_200_OK)
async def switch_organization(
    data: SwitchOrganizationRequest,
    session: AsyncSession = Depends(get_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
    lang: str = Depends(get_language),
) -> GenericResponse[dict[str, str]]:
    """Re-issues a JWT for a different organization the user belongs to."""
    user_id = UUID(str(payload["sub"]))
    token = await AuthService.switch_organization(session, user_id, data.organization_id)
    success_msg = i18n.t("success.organization_switched", lang=lang)
    return GenericResponse(data={"access_token": token, "token_type": "bearer"}, message=success_msg)


@router.post("/forgot-password", response_model=GenericResponse[Any], status_code=status.HTTP_200_OK)
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    lang: str = Depends(get_language),
) -> GenericResponse[Any]:
    """Generates a password reset token and emails it if the user exists."""
    token = await AuthService.forgot_password(session, data.email)

    if token:
        background_tasks.add_task(EmailService.send_password_reset_email, email=data.email, token=token, lang=lang)

    success_msg = i18n.t("success.password_reset_email_sent", lang=lang)
    return GenericResponse[Any](data=None, message=success_msg)


@router.post("/reset-password", response_model=GenericResponse[Any], status_code=status.HTTP_200_OK)
async def reset_password(
    data: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
    lang: str = Depends(get_language),
) -> GenericResponse[Any]:
    """Consumes a reset token to update the user's password."""
    await AuthService.reset_password(session, data.token, data.new_password)

    success_msg = i18n.t("success.password_reset_successful", lang=lang)
    return GenericResponse[Any](data=None, message=success_msg)


@router.post("/change-password", response_model=GenericResponse[Any], status_code=status.HTTP_200_OK)
async def change_password(
    data: ChangePasswordRequest,
    session: AsyncSession = Depends(get_session),
    payload: dict[str, Any] = Depends(get_jwt_payload),
    lang: str = Depends(get_language),
) -> GenericResponse[Any]:
    """Allows an authenticated user to change their password."""
    user_id = UUID(str(payload["sub"]))
    await AuthService.change_password(session, user_id, data.current_password, data.new_password)

    success_msg = i18n.t("success.password_changed", lang=lang)
    return GenericResponse[Any](data=None, message=success_msg)
