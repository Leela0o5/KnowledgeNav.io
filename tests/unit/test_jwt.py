import pytest

from knowledge_nav.auth.jwt import InvalidTokenError, issue_access_token, verify_access_token


def test_issue_and_verify_access_token() -> None:
    token = issue_access_token("user-123", "user")
    claims = verify_access_token(token)
    assert claims["sub"] == "user-123"
    assert claims["role"] == "user"


def test_verify_invalid_token_raises() -> None:
    with pytest.raises(InvalidTokenError):
        verify_access_token("not.a.real.token")


def test_verify_wrong_type_raises() -> None:
    import time
    from datetime import UTC, datetime, timedelta
    from jose import jwt
    from knowledge_nav.config import settings

    payload = {
        "sub": "user-123",
        "role": "user",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=15),
        "type": "refresh",
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    with pytest.raises(InvalidTokenError):
        verify_access_token(token)
