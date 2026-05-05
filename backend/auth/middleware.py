import uuid
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth.jwt import InvalidTokenError, verify_access_token
from auth.models import User
from src.config import settings
from src.db import get_db

_AT_COOKIE = "__Secure-at" if settings.OAUTH_REDIRECT_BASE_URL.startswith("https") else "knav_at"


class PermissionDeniedError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


async def get_current_user(
    access_token: Annotated[str | None, Cookie(alias=_AT_COOKIE)] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        claims = verify_access_token(access_token)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == uuid.UUID(claims["sub"])))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(*roles: str):  # type: ignore[no-untyped-def]
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise PermissionDeniedError
        return current_user
    return dependency


require_corpus_admin = require_role("corpus_admin", "admin")
require_admin = require_role("admin")
