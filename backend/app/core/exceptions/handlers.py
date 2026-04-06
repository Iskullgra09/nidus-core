from typing import Dict, List

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.base import NidusException
from app.core.i18n.service import i18n


def _get_lang(request: Request) -> str:
    """
    Private helper to extract the preferred language from the request headers.
    """
    accept_lang: str = request.headers.get("accept-language", "en")
    return accept_lang.split(",")[0].split("-")[0].lower()


async def nidus_exception_handler(request: Request, exc: NidusException) -> JSONResponse:
    """
    Global handler for NidusException.
    Detects language from headers and returns a localized JSON response.
    """
    lang: str = _get_lang(request)

    translated_message: str = i18n.t(exc.message_key, lang=lang, **exc.params)

    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "code": exc.code, "message": translated_message, "data": exc.params if exc.params else None},
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Captures raw database errors and returns a generic, localized safe message.
    """
    print(f"DB Error: {exc}")

    lang: str = _get_lang(request)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "DATABASE_ERROR",
            "message": i18n.t("common.internal_error", lang=lang),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Captures Pydantic validation errors (422) and translates them.
    """
    lang: str = _get_lang(request)

    translated_errors: List[Dict[str, str]] = []

    for err in exc.errors():
        raw_msg: str = str(err.get("msg", "")).replace("Value error, ", "")

        translated_msg: str = i18n.t(raw_msg, lang=lang)

        translated_errors.append(
            {
                "field": ".".join(map(str, err.get("loc", []))),
                "message": translated_msg,
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "code": "VALIDATION_FAILED",
            "message": i18n.t("common.validation_error", lang=lang),
            "data": {"errors": translated_errors},
        },
    )


async def global_500_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    The Absolute Catch-All. Captures ANY unhandled Python exception,
    prevents server crashes, and returns a safe, localized JSON response.
    """
    print(f"CRITICAL SYSTEM ERROR: {exc}")

    lang: str = _get_lang(request)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": i18n.t("common.internal_error", lang=lang),
        },
    )
