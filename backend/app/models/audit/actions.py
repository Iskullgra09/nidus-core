from enum import StrEnum


class AuditAction(StrEnum):
    """Canonical audit action codes. Pattern: resource.verb"""

    AUTH_LOGIN = "auth.login"
    AUTH_SELECT_ORG = "auth.select_org"
    AUTH_SWITCH_ORG = "auth.switch_org"

    ORG_CREATE = "organization.create"
    ORG_UPDATE = "organization.update"
    ORG_DELETE = "organization.delete"

    INVITATION_CREATE = "invitation.create"
    INVITATION_ACCEPT = "invitation.accept"
    INVITATION_REVOKE = "invitation.revoke"

    ROLE_CREATE = "role.create"
    ROLE_UPDATE = "role.update"
    ROLE_DELETE = "role.delete"

    MEMBER_ROLE_UPDATE = "member.role_update"
    MEMBER_REMOVE = "member.remove"


class AuditResourceType(StrEnum):
    ORGANIZATION = "organization"
    INVITATION = "invitation"
    ROLE = "role"
    MEMBER = "member"
    USER = "user"
    SESSION = "session"
