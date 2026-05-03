import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_nav.sessions.models import Message, Session


class SessionNotFoundError(Exception):
    def __init__(self, session_id: uuid.UUID) -> None:
        super().__init__(f"Session {session_id} not found")
        self.session_id = session_id


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, user_id: uuid.UUID, corpus_id: str, title: str | None = None) -> Session:
        now = datetime.now(UTC)
        session = Session(
            user_id=user_id,
            corpus_id=corpus_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        self._db.add(session)
        await self._db.commit()
        await self._db.refresh(session)
        return session

    async def get(self, session_id: uuid.UUID) -> Session | None:
        result = await self._db.execute(select(Session).where(Session.id == session_id))
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID, limit: int = 50) -> list[Session]:
        result = await self._db.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(Session.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars())

    async def delete(self, session_id: uuid.UUID) -> None:
        result = await self._db.execute(select(Session).where(Session.id == session_id))
        session = result.scalar_one_or_none()
        if session is not None:
            await self._db.delete(session)
            await self._db.commit()

    async def get_recent_messages(self, session_id: uuid.UUID, limit: int) -> list[Message]:
        result = await self._db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))

    async def list_messages(
        self,
        session_id: uuid.UUID,
        cursor: str | None = None,
        limit: int = 50,
    ) -> tuple[list[Message], str | None]:
        query = select(Message).where(Message.session_id == session_id)
        if cursor is not None:
            cursor_ts, cursor_id = cursor.split(":")
            query = query.where(
                Message.created_at < datetime.fromisoformat(cursor_ts)
            )
        query = query.order_by(Message.created_at.desc()).limit(limit + 1)
        result = await self._db.execute(query)
        rows = list(result.scalars())
        has_more = len(rows) > limit
        items = list(reversed(rows[:limit]))
        next_cursor: str | None = None
        if has_more and items:
            first = items[0]
            next_cursor = f"{first.created_at.isoformat()}:{first.id}"
        return items, next_cursor

    async def append_message(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str,
        citations: list[Any] | None = None,
        citation_coverage: float | None = None,
        trace_id: str | None = None,
    ) -> Message:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            citations=citations,
            citation_coverage=citation_coverage,
            trace_id=trace_id,
            created_at=datetime.now(UTC),
        )
        self._db.add(message)
        await self._db.execute(
            update(Session).where(Session.id == session_id).values(updated_at=func.now())
        )
        await self._db.commit()
        await self._db.refresh(message)
        return message
