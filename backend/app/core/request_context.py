"""Per-request context for observability and audit (contextvars, no globals)."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional
from uuid import UUID

_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
_client_ip: ContextVar[Optional[str]] = ContextVar("client_ip", default=None)
_actor_user_id: ContextVar[Optional[UUID]] = ContextVar("actor_user_id", default=None)
_organization_id: ContextVar[Optional[UUID]] = ContextVar("organization_id", default=None)


class RequestContext:
    """Typed accessors around request-scoped contextvars."""

    @staticmethod
    def reset() -> None:
        _request_id.set(None)
        _client_ip.set(None)
        _actor_user_id.set(None)
        _organization_id.set(None)

    @staticmethod
    def set_request_id(value: str) -> None:
        _request_id.set(value)

    @staticmethod
    def get_request_id() -> Optional[str]:
        return _request_id.get()

    @staticmethod
    def set_client_ip(value: Optional[str]) -> None:
        _client_ip.set(value)

    @staticmethod
    def get_client_ip() -> Optional[str]:
        return _client_ip.get()

    @staticmethod
    def set_actor(user_id: Optional[UUID]) -> None:
        _actor_user_id.set(user_id)

    @staticmethod
    def get_actor() -> Optional[UUID]:
        return _actor_user_id.get()

    @staticmethod
    def set_organization(organization_id: Optional[UUID]) -> None:
        _organization_id.set(organization_id)

    @staticmethod
    def get_organization() -> Optional[UUID]:
        return _organization_id.get()
