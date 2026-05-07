import uuid

import pytest
from jose import jwt as jose_jwt

from auth.jwt import InvalidTokenError, issue_access_token, verify_access_token
from src.config import settings


def test_issue_and_verify_access_token() -> None:
    user_id = str(uuid.uuid4())
    token = issue_access_token(user_id, "user")
    claims = verify_access_token(token)
    assert claims["sub"] == user_id
    assert claims["role"] == "user"


def test_verify_invalid_token_raises() -> None:
    with pytest.raises(InvalidTokenError):
        verify_access_token("not-a-valid-token")


def test_verify_wrong_type_raises() -> None:
    payload = {"sub": str(uuid.uuid4()), "role": "user", "type": "refresh"}
    bad_token = jose_jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    with pytest.raises(InvalidTokenError):
        verify_access_token(bad_token)


def test_different_users_get_different_tokens() -> None:
    t1 = issue_access_token(str(uuid.uuid4()), "user")
    t2 = issue_access_token(str(uuid.uuid4()), "user")
    assert t1 != t2
