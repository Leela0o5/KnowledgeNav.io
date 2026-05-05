import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth.middleware import get_current_user
from auth.models import User
from src.db import get_db
from sessions.repository import SessionRepository

router = APIRouter(prefix="/api/v1/sessions", tags=["messages"])


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: Any
    citation_coverage: float | None
    trace_id: str | None
    created_at: datetime


class MessageListResponse(BaseModel):
    data: list[MessageResponse]
    next_cursor: str | None
    has_more: bool


@router.get("/{session_id}/messages", response_model=MessageListResponse)
async def list_messages(
    session_id: uuid.UUID,
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageListResponse:
    repo = SessionRepository(db)
    session = await repo.get(session_id)
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    messages, next_cursor = await repo.list_messages(session_id, cursor, limit)
    return MessageListResponse(
        data=[
            MessageResponse(
                id=str(m.id),
                session_id=str(m.session_id),
                role=m.role,
                content=m.content,
                citations=m.citations,
                citation_coverage=m.citation_coverage,
                trace_id=m.trace_id,
                created_at=m.created_at,
            )
            for m in messages
        ],
        next_cursor=next_cursor,
        has_more=next_cursor is not None,
    )
