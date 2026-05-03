import json
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from knowledge_nav.auth.middleware import get_current_user
from knowledge_nav.auth.models import User
from knowledge_nav.config import settings
from knowledge_nav.db import get_db
from knowledge_nav.sessions.repository import SessionRepository

router = APIRouter(prefix="/api/v1", tags=["query"])


async def _event_stream(
    question: str,
    session_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
    repo = SessionRepository(db)
    session = await repo.get(session_id)
    if session is None or session.user_id != current_user.id:
        yield f"event: error\ndata: Session not found\n\n"
        return

    recent_messages = await repo.get_recent_messages(session_id, limit=settings.SESSION_CONTEXT_TURNS * 2)
    await repo.append_message(session_id, "user", question)

    from knowledge_nav.agent.graph import build_rag_graph
    from knowledge_nav.sessions.context import build_conversation_context

    graph = build_rag_graph()
    trace_id = str(uuid.uuid4())
    conversation_context = build_conversation_context(recent_messages)

    initial_state = {
        "question": question,
        "corpus_id": session.corpus_id,
        "session_id": str(session_id),
        "user_id": str(current_user.id),
        "conversation_context": conversation_context,
        "bm25_results": [],
        "vector_results": [],
        "fused_results": [],
        "reranked_chunks": [],
        "raw_answer": "",
        "validated_answer": None,
        "citation_attempts": 0,
        "trace_id": trace_id,
        "error": None,
    }

    final_state = await graph.ainvoke(initial_state)
    validated = final_state.get("validated_answer")

    if validated is None:
        yield f"event: error\ndata: Generation failed\n\n"
        return

    for word in validated.content.split():
        yield f"event: token\ndata: {word} \n\n"

    citations_data = [
        {
            "chunk_id": c.chunk_id,
            "source_file": c.source_file,
            "page_range": c.page_range,
            "excerpt": c.excerpt,
        }
        for c in validated.citations
    ]

    await repo.append_message(
        session_id,
        "assistant",
        validated.content,
        citations=citations_data,
        citation_coverage=validated.citation_coverage,
        trace_id=trace_id,
    )

    done_payload = json.dumps({
        "answer": validated.content,
        "citations": citations_data,
        "trace_id": trace_id,
        "citation_coverage": validated.citation_coverage,
        "warning": validated.warning,
    })
    yield f"event: done\ndata: {done_payload}\n\n"


@router.get("/query")
async def query(
    question: str = Query(..., min_length=1),
    session_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    return StreamingResponse(
        _event_stream(question, session_id, current_user, db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
