from app.core.exceptions.base import ConflictError, EntityNotFoundError
from app.models.identity.role import Role
from app.models.identity.scopes import DEFAULT_ROLE_NAMES, NidusScope
from app.schemas.responses.identity import RoleResponse


def to_role_response(role: Role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        scopes=role.scopes,
        is_system=role.name in DEFAULT_ROLE_NAMES,
    )


def validate_custom_role_name(name: str) -> None:
    if name in DEFAULT_ROLE_NAMES:
        raise ConflictError(message_key="role.reserved_name", name=name)


def validate_scopes(scopes: list[str]) -> None:
    invalid = [scope for scope in scopes if not NidusScope.is_assignable(scope)]
    if invalid:
        raise ConflictError(message_key="role.invalid_scopes", scopes=", ".join(invalid))


def ensure_custom_role(role: Role | None) -> Role:
    if not role or role.deleted_at is not None:
        raise EntityNotFoundError(entity="role")
    if role.name in DEFAULT_ROLE_NAMES:
        raise ConflictError(message_key="role.system_role_protected")
    return role
