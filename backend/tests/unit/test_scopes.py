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
