from enum import StrEnum
from typing import Set


class NidusScope(StrEnum):
    """
    Hierarchical Scope Registry for Nidus.
    Pattern: module:resource:action
    """

    # --- System Scopes ---
    SUPERADMIN = "*"  # God Mode

    # --- Organization Scopes ---
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"

    # --- Member/User Scopes ---
    MEMBER_READ = "identity:member:read"
    MEMBER_WRITE = "identity:member:write"
    MEMBER_INVITE = "identity:member:invite"

    # --- Role Scopes ---
    ROLE_READ = "identity:role:read"
    ROLE_WRITE = "identity:role:write"

    @classmethod
    def get_implied_scopes(cls, scope: str) -> Set[str]:
        """
        Logic for implicit permissions.
        Example: 'write' usually implies 'read'.
        """
        permissions = {scope}
        if ":write" in scope:
            permissions.add(scope.replace(":write", ":read"))
        if ":invite" in scope:
            permissions.add(scope.replace(":invite", ":read"))
        return permissions
