from typing import Any, Dict


class NidusException(Exception):
    """
    Master business exception. Fully compatible with Pylance Strict.
    """

    def __init__(self, code: str, message_key: str, status_code: int = 400, **kwargs: Any) -> None:
        self.code: str = code
        self.message_key: str = message_key
        self.status_code: int = status_code
        self.params: Dict[str, Any] = kwargs
        super().__init__(self.message_key)


class AuthenticationError(NidusException):
    """Raised when credentials or tokens are invalid."""

    def __init__(self, message_key: str = "common.unauthorized", **kwargs: Any) -> None:
        super().__init__(code="UNAUTHORIZED", message_key=message_key, status_code=401, **kwargs)


class EntityNotFoundError(NidusException):
    """Raised when a requested resource (User, Org, Invite) is missing."""

    def __init__(self, entity: str, **kwargs: Any) -> None:
        super().__init__(
            code=f"{entity.upper()}_NOT_FOUND",
            message_key="common.not_found",
            status_code=404,
            **kwargs,
        )


class ConflictError(NidusException):
    """Raised when there is a data conflict (e.g., duplicate slug/email)."""

    def __init__(self, message_key: str, **kwargs: Any) -> None:
        super().__init__(code="DATA_CONFLICT", message_key=message_key, status_code=409, **kwargs)
