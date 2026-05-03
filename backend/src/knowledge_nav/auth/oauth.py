import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urlencode
import hashlib
import base64

import httpx
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from knowledge_nav.auth.jwt import InvalidTokenError, issue_access_token, issue_refresh_token
from knowledge_nav.auth.models import OAuthAccount, User
from knowledge_nav.config import settings


class InvalidStateError(Exception):
    pass


@dataclass(frozen=True)
class OAuthConfig:
    authorization_url: str
    token_url: str
    userinfo_url: str
    scopes: list[str]


@dataclass(frozen=True)
class ProviderTokens:
    access_token: str


@dataclass(frozen=True)
class UserInfo:
    provider_id: str
    email: str
    name: str
    avatar_url: str | None


PROVIDER_CONFIGS: dict[str, OAuthConfig] = {
    "google": OAuthConfig(
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://www.googleapis.com/oauth2/v3/userinfo",
        scopes=["openid", "email", "profile"],
    ),
    "github": OAuthConfig(
        authorization_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        userinfo_url="https://api.github.com/user",
        scopes=["read:user", "user:email"],
    ),
}

_CLIENT_CREDENTIALS: dict[str, dict[str, str]] = {
    "google": {"client_id": settings.GOOGLE_CLIENT_ID, "client_secret": settings.GOOGLE_CLIENT_SECRET},
    "github": {"client_id": settings.GITHUB_CLIENT_ID, "client_secret": settings.GITHUB_CLIENT_SECRET},
}


def _generate_pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def _build_authorization_url(provider: str, config: OAuthConfig, challenge: str, state: str) -> str:
    creds = _CLIENT_CREDENTIALS[provider]
    params: dict[str, str] = {
        "client_id": creds["client_id"],
        "redirect_uri": f"{settings.OAUTH_REDIRECT_BASE_URL}/auth/callback/{provider}",
        "response_type": "code",
        "scope": " ".join(config.scopes),
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    return f"{config.authorization_url}?{urlencode(params)}"


async def begin_oauth_flow(provider: str, redis: Redis) -> str:  # type: ignore[type-arg]
    if provider not in PROVIDER_CONFIGS:
        raise ValueError(f"Unknown provider: {provider}")
    config = PROVIDER_CONFIGS[provider]
    verifier, challenge = _generate_pkce_pair()
    state = secrets.token_urlsafe(32)
    await redis.setex(f"pkce:{state}", 300, verifier)
    return _build_authorization_url(provider, config, challenge, state)


async def _exchange_code(config: OAuthConfig, provider: str, code: str, verifier: str) -> ProviderTokens:
    creds = _CLIENT_CREDENTIALS[provider]
    async with httpx.AsyncClient() as client:
        response = await client.post(
            config.token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{settings.OAUTH_REDIRECT_BASE_URL}/auth/callback/{provider}",
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "code_verifier": verifier,
            },
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
    return ProviderTokens(access_token=data["access_token"])


async def _fetch_userinfo(config: OAuthConfig, provider: str, access_token: str) -> UserInfo:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            config.userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        data = response.json()

    if provider == "google":
        return UserInfo(
            provider_id=data["sub"],
            email=data["email"],
            name=data.get("name", data["email"]),
            avatar_url=data.get("picture"),
        )
    if provider == "github":
        return UserInfo(
            provider_id=str(data["id"]),
            email=data.get("email") or f"{data['login']}@users.noreply.github.com",
            name=data.get("name") or data["login"],
            avatar_url=data.get("avatar_url"),
        )
    raise ValueError(f"Unknown provider: {provider}")


async def _upsert_user(db: AsyncSession, provider: str, info: UserInfo) -> User:
    result = await db.execute(
        select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_id == info.provider_id,
        )
    )
    oauth_account = result.scalar_one_or_none()

    if oauth_account is not None:
        user_result = await db.execute(select(User).where(User.id == oauth_account.user_id))
        user = user_result.scalar_one()
        user.name = info.name
        user.avatar_url = info.avatar_url
        await db.commit()
        await db.refresh(user)
        return user

    user_result = await db.execute(select(User).where(User.email == info.email))
    user = user_result.scalar_one_or_none()
    if user is None:
        user = User(
            email=info.email,
            name=info.name,
            avatar_url=info.avatar_url,
            role="user",
            created_at=datetime.now(UTC),
        )
        db.add(user)
        await db.flush()

    new_account = OAuthAccount(
        user_id=user.id,
        provider=provider,
        provider_id=info.provider_id,
    )
    db.add(new_account)
    await db.commit()
    await db.refresh(user)
    return user


async def complete_oauth_flow(
    provider: str,
    code: str,
    state: str,
    redis: Redis,  # type: ignore[type-arg]
    db: AsyncSession,
) -> tuple[str, str]:
    verifier = await redis.getdel(f"pkce:{state}")
    if verifier is None:
        raise InvalidStateError
    if provider not in PROVIDER_CONFIGS:
        raise InvalidTokenError
    config = PROVIDER_CONFIGS[provider]
    provider_tokens = await _exchange_code(config, provider, code, verifier)
    userinfo = await _fetch_userinfo(config, provider, provider_tokens.access_token)
    user = await _upsert_user(db, provider, userinfo)
    access_token = issue_access_token(str(user.id), user.role)
    refresh_token = await issue_refresh_token(db, uuid.UUID(str(user.id)))
    return access_token, refresh_token
