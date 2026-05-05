import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth.models import RefreshToken, User
from src.config import settings


class InvalidTokenError(Exception):
    pass


class TokenRevokedError(Exception):
    pass


def issue_access_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def verify_access_token(token: str) -> dict[str, str]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise InvalidTokenError
        return {"sub": payload["sub"], "role": payload.get("role", "user")}
    except JWTError as exc:
        raise InvalidTokenError from exc


async def issue_refresh_token(db: AsyncSession, user_id: uuid.UUID) -> str:
    raw = secrets.token_urlsafe(64)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    expires_at = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(record)
    await db.commit()
    return raw


async def rotate_refresh_token(db: AsyncSession, raw_token: str) -> tuple[str, str, str]:
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()
    if record is None or record.revoked_at is not None:
        raise TokenRevokedError
    if record.expires_at < datetime.now(UTC):
        raise InvalidTokenError

    record.revoked_at = datetime.now(UTC)
    await db.commit()

    user_result = await db.execute(select(User).where(User.id == record.user_id))
    user = user_result.scalar_one()

    new_access = issue_access_token(str(user.id), user.role)
    new_refresh = await issue_refresh_token(db, user.id)
    return new_access, new_refresh, str(user.id)


async def revoke_refresh_token(db: AsyncSession, raw_token: str) -> None:
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()
    if record is not None and record.revoked_at is None:
        record.revoked_at = datetime.now(UTC)
        await db.commit()
