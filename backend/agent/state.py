from typing import TypedDict

from citation.schema import AnswerWithCitations
from retrieval.schema import ScoredChunk


class RAGState(TypedDict):
    question: str
    corpus_id: str
    session_id: str
    user_id: str
    conversation_context: str
    bm25_results: list[ScoredChunk]
    vector_results: list[ScoredChunk]
    fused_results: list[ScoredChunk]
    reranked_chunks: list[ScoredChunk]
    raw_answer: str
    validated_answer: AnswerWithCitations | None
    citation_attempts: int
    trace_id: str
    error: str | None
