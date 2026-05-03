import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_nav.auth.middleware import get_current_user
from knowledge_nav.auth.models import User
from knowledge_nav.db import get_db
from knowledge_nav.sessions.repository import SessionNotFoundError, SessionRepository

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


class SessionResponse(BaseModel):
    id: str
    corpus_id: str
    title: str | None
    created_at: datetime
    updated_at: datetime


class CreateSessionBody(BaseModel):
    corpus_id: str
    title: str | None = None


class SessionListResponse(BaseModel):
    data: list[SessionResponse]
    has_more: bool


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SessionListResponse:
    repo = SessionRepository(db)
    sessions = await repo.list_for_user(current_user.id)
    return SessionListResponse(
        data=[
            SessionResponse(
                id=str(s.id),
                corpus_id=s.corpus_id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in sessions
        ],
        has_more=len(sessions) == 50,
    )


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: CreateSessionBody,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    repo = SessionRepository(db)
    session = await repo.create(current_user.id, body.corpus_id, body.title)
    return SessionResponse(
        id=str(session.id),
        corpus_id=session.corpus_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    repo = SessionRepository(db)
    session = await repo.get(session_id)
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return SessionResponse(
        id=str(session.id),
        corpus_id=session.corpus_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = SessionRepository(db)
    session = await repo.get(session_id)
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    await repo.delete(session_id)
