import pytest

from app.models.identity.scopes import NidusScope


@pytest.mark.parametrize(
    ("user_scopes", "required", "expected"),
    [
        ([NidusScope.SUPERADMIN.value], NidusScope.ROLE_WRITE.value, True),
        ([NidusScope.MEMBER_WRITE.value], NidusScope.MEMBER_READ.value, True),
        ([NidusScope.MEMBER_INVITE.value], NidusScope.MEMBER_READ.value, True),
        ([NidusScope.MEMBER_READ.value], NidusScope.MEMBER_WRITE.value, False),
        ([NidusScope.MEMBER_READ.value], NidusScope.MEMBER_READ.value, True),
        ([NidusScope.ORG_READ.value], NidusScope.MEMBER_READ.value, False),
    ],
)
def test_grants_access(user_scopes: list[str], required: str, expected: bool) -> None:
    assert NidusScope.grants_access(user_scopes, required) is expected


def test_scope_group() -> None:
    assert NidusScope.scope_group("identity:member:read") == "identity:member"
    assert NidusScope.scope_group("org:read") == "org"
    assert NidusScope.scope_group(NidusScope.AUDIT_READ.value) == "audit"


def test_audit_read_not_implied_by_org_read() -> None:
    assert NidusScope.grants_access([NidusScope.ORG_READ.value], NidusScope.AUDIT_READ.value) is False
    assert NidusScope.grants_access([NidusScope.AUDIT_READ.value], NidusScope.AUDIT_READ.value) is True
    assert NidusScope.grants_access([NidusScope.SUPERADMIN.value], NidusScope.AUDIT_READ.value) is True


@pytest.mark.parametrize("scope", NidusScope.assignable_scopes())
def test_assignable_scopes_include_audit_read(scope: str) -> None:
    assert scope != NidusScope.SUPERADMIN.value


def test_audit_read_is_assignable() -> None:
    assert NidusScope.AUDIT_READ.value in NidusScope.assignable_scopes()

