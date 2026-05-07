from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt import (
    InvalidTokenError,
    TokenRevokedError,
    revoke_refresh_token,
    rotate_refresh_token,
)
from auth.middleware import get_current_user
from auth.models import User
from auth.oauth import InvalidStateError, begin_oauth_flow, complete_oauth_flow
from src.config import settings
from src.db import get_db
from src.redis_client import get_redis

router = APIRouter(prefix="/auth", tags=["auth"])

_AT_COOKIE = "__Secure-at"
_RT_COOKIE = "__Secure-rt"
_COOKIE_KWARGS = {
    "httponly": True,
    "samesite": "none",
    "secure": True,
}


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str | None
    role: str


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
    )


@router.post("/refresh")
async def refresh_tokens(
    response: Response,
    refresh_token_cookie: str | None = Cookie(None, alias=_RT_COOKIE),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if refresh_token_cookie is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    try:
        new_access, new_refresh, _ = await rotate_refresh_token(db, refresh_token_cookie)
    except (TokenRevokedError, InvalidTokenError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    response.set_cookie(_AT_COOKIE, new_access, max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60, **_COOKIE_KWARGS)
    response.set_cookie(_RT_COOKIE, new_refresh, max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400, **_COOKIE_KWARGS)
    return {"status": "refreshed"}


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token_cookie: str | None = Cookie(None, alias=_RT_COOKIE),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if refresh_token_cookie is not None:
        await revoke_refresh_token(db, refresh_token_cookie)
    response.delete_cookie(_AT_COOKIE)
    response.delete_cookie(_RT_COOKIE)
    return {"status": "logged_out"}


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    state: str,
    code: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
) -> RedirectResponse:
    if error or not code:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/?error=access_denied", status_code=302)
    try:
        access_token, refresh_token = await complete_oauth_flow(provider, code, state, redis, db)
    except InvalidStateError:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/?error=invalid_state", status_code=302)
    except InvalidTokenError:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/?error=token_failed", status_code=302)

    redirect = RedirectResponse(url=f"{settings.FRONTEND_URL}/chat", status_code=302)
    redirect.set_cookie(_AT_COOKIE, access_token, max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60, **_COOKIE_KWARGS)
    redirect.set_cookie(_RT_COOKIE, refresh_token, max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400, **_COOKIE_KWARGS)
    return redirect


@router.get("/{provider}")
async def begin_login(provider: str, redis=Depends(get_redis)) -> RedirectResponse:
    try:
        redirect_url = await begin_oauth_flow(provider, redis)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RedirectResponse(url=redirect_url)
