from enum import StrEnum
from typing import Any, Dict, Iterable, Set


class NidusScope(StrEnum):
    """
    Hierarchical Scope Registry for Nidus.
    Pattern: module:resource:action
    """

    SUPERADMIN = "*"

    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"

    MEMBER_READ = "identity:member:read"
    MEMBER_WRITE = "identity:member:write"
    MEMBER_INVITE = "identity:member:invite"

    ROLE_READ = "identity:role:read"
    ROLE_WRITE = "identity:role:write"

    @classmethod
    def get_implied_scopes(cls, scope: str) -> Set[str]:
        """Calculates implicit permissions granted by holding a scope (write → read, invite → read)."""
        permissions = {scope}
        if ":write" in scope:
            permissions.add(scope.replace(":write", ":read"))
        if ":invite" in scope:
            permissions.add(scope.replace(":invite", ":read"))
        return permissions

    @classmethod
    def grants_access(cls, user_scopes: Iterable[str], required: str) -> bool:
        """Returns True when any held scope satisfies the required scope."""
        scope_set = set(user_scopes)

        if cls.SUPERADMIN in scope_set:
            return True

        if required in scope_set:
            return True

        return any(required in cls.get_implied_scopes(held) for held in scope_set)

    @classmethod
    def scope_group(cls, scope: str) -> str:
        """UI grouping key: `identity:member:read` → `identity:member`."""
        parts = scope.split(":")
        if len(parts) >= 2:
            return ":".join(parts[:-1])
        return parts[0]

    @classmethod
    def assignable_scopes(cls) -> list[str]:
        """Scopes that can be assigned to custom roles (excludes wildcard)."""
        return [scope.value for scope in cls if scope != cls.SUPERADMIN]

    @classmethod
    def is_assignable(cls, scope: str) -> bool:
        return scope in cls.assignable_scopes()


class DefaultRole(StrEnum):
    """Standard roles created automatically for every new organization."""

    OWNER = "Owner"
    ADMIN = "Admin"
    MEMBER = "Member"
    VIEWER = "Viewer"


DEFAULT_ROLE_NAMES = {role.value for role in DefaultRole}


DEFAULT_ROLES_CONFIG: Dict[DefaultRole, Dict[str, Any]] = {
    DefaultRole.OWNER: {
        "description": "Full access to the organization, including billing and workspace deletion.",
        "scopes": [NidusScope.SUPERADMIN],
    },
    DefaultRole.ADMIN: {
        "description": "Can manage members, roles, and general organization settings.",
        "scopes": [
            NidusScope.ORG_READ,
            NidusScope.ORG_UPDATE,
            NidusScope.MEMBER_READ,
            NidusScope.MEMBER_WRITE,
            NidusScope.MEMBER_INVITE,
            NidusScope.ROLE_READ,
            NidusScope.ROLE_WRITE,
        ],
    },
    DefaultRole.MEMBER: {
        "description": "Standard collaborator. Can view the organization and fellow members.",
        "scopes": [NidusScope.ORG_READ, NidusScope.MEMBER_READ],
    },
    DefaultRole.VIEWER: {
        "description": "Read-only access for auditing or consultation purposes.",
        "scopes": [NidusScope.ORG_READ],
    },
}
