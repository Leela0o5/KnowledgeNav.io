from typing import Literal

from groq import AsyncGroq

from agent.prompts import STRICT_CITATION_PROMPT, SYSTEM_PROMPT, build_user_prompt
from agent.state import RAGState
from citation.enforcer import CitationEnforcer, extract_citation_ids
from citation.schema import AnswerWithCitations, Citation
from src.config import settings
from retrieval.hybrid import reciprocal_rank_fusion
from retrieval.reranker import CohereReranker
from retrieval.schema import ScoredChunk
from sessions.context import format_context_for_prompt


_enforcer = CitationEnforcer(min_coverage=settings.MIN_CITATION_COVERAGE)


async def analyse_query(state: RAGState) -> RAGState:
    return state


async def hybrid_retrieve(
    state: RAGState,
    bm25_retrieve: object,
    vector_retrieve: object,
) -> RAGState:
    from retrieval.bm25_retriever import BM25Retriever
    from retrieval.vector_retriever import VectorRetriever

    bm25_retriever = bm25_retrieve  # type: ignore[assignment]
    vector_retriever = vector_retrieve  # type: ignore[assignment]

    bm25_results: list[ScoredChunk] = []
    vector_results: list[ScoredChunk] = []

    if isinstance(bm25_retriever, BM25Retriever):
        bm25_results = bm25_retriever.retrieve(state["question"], top_k=settings.BM25_TOP_K)
    if isinstance(vector_retriever, VectorRetriever):
        vector_results = await vector_retriever.retrieve(state["question"], top_k=settings.VECTOR_TOP_K)

    fused = reciprocal_rank_fusion(bm25_results, vector_results, k=settings.RRF_K)
    return {**state, "bm25_results": bm25_results, "vector_results": vector_results, "fused_results": fused}


async def rerank(state: RAGState, reranker: CohereReranker) -> RAGState:
    reranked = await reranker.rerank(state["question"], state["fused_results"])
    return {**state, "reranked_chunks": reranked}


async def inject_chat_history(state: RAGState) -> RAGState:
    enriched_question = format_context_for_prompt([], state["question"])
    if state.get("conversation_context"):
        enriched_question = f"[Previous conversation]\n{state['conversation_context']}\n\n[Current question]\n{state['question']}"
    return {**state, "question": enriched_question}


async def generate_with_citations(state: RAGState) -> RAGState:
    client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    attempt = state.get("citation_attempts", 0)
    system = STRICT_CITATION_PROMPT if attempt > 0 else SYSTEM_PROMPT
    chunk_pairs = [(c.chunk.id, c.chunk.text) for c in state["reranked_chunks"]]
    user_message = build_user_prompt(state["question"], chunk_pairs, state.get("conversation_context", ""))

    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        max_tokens=2048,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
    )
    raw_answer = response.choices[0].message.content or ""
    return {**state, "raw_answer": raw_answer}


async def validate_citations(state: RAGState) -> RAGState:
    valid_ids = {c.chunk.id for c in state["reranked_chunks"]}
    result = _enforcer.validate(state["raw_answer"], valid_ids)

    cited_ids = extract_citation_ids(state["raw_answer"])
    chunk_map = {c.chunk.id: c.chunk for c in state["reranked_chunks"]}
    citations = [
        Citation(
            chunk_id=cid,
            source_file=chunk_map[cid].source_file,
            page_range=chunk_map[cid].page_range,
            excerpt=chunk_map[cid].text[:150],
        )
        for cid in cited_ids
        if cid in chunk_map
    ]

    answer = AnswerWithCitations(
        content=state["raw_answer"],
        citations=citations,
        citation_coverage=result.coverage,
        is_valid=result.is_valid,
        warning=None if result.is_valid else "Citation coverage below threshold",
    )
    return {**state, "validated_answer": answer, "citation_attempts": state.get("citation_attempts", 0) + 1}


async def persist_message(state: RAGState) -> RAGState:
    return state


async def handle_error(state: RAGState) -> RAGState:
    error_msg = state.get("error") or "Maximum citation retries exceeded"
    fallback = AnswerWithCitations(
        content=state.get("raw_answer", "Unable to generate a fully cited answer."),
        citations=[],
        citation_coverage=0.0,
        is_valid=False,
        warning=error_msg,
    )
    return {**state, "validated_answer": fallback, "error": error_msg}


def citation_gate(state: RAGState) -> Literal["pass", "retry", "fail"]:
    answer = state.get("validated_answer")
    if answer is not None and answer.is_valid:
        return "pass"
    attempts = state.get("citation_attempts", 0)
    if attempts < settings.CITATION_RETRY_LIMIT:
        return "retry"
    return "fail"
