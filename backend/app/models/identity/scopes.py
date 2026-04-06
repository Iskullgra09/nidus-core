from enum import StrEnum
from typing import Any, Dict, Set


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
        """Calculates implicit permissions (e.g., write implies read)."""
        permissions = {scope}
        if ":write" in scope:
            permissions.add(scope.replace(":write", ":read"))
        if ":invite" in scope:
            permissions.add(scope.replace(":invite", ":read"))
        return permissions


class DefaultRole(StrEnum):
    """Standard roles created automatically for every new organization."""

    OWNER = "Owner"
    ADMIN = "Admin"
    MEMBER = "Member"
    VIEWER = "Viewer"


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
    DefaultRole.VIEWER: {"description": "Read-only access for auditing or consultation purposes.", "scopes": [NidusScope.ORG_READ]},
}
