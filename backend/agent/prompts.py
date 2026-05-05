SYSTEM_PROMPT = """You are a precise assistant. Answer using ONLY the provided context chunks.

For every factual claim, include an inline citation: [SOURCE:chunk_id]
Multiple sources for one sentence: [SOURCE:id1][SOURCE:id2]
If context is insufficient, respond: "The provided documents do not contain enough information to answer this question."
Do not speculate. Do not use knowledge outside the provided chunks."""

STRICT_CITATION_PROMPT = """You are a precise assistant. You MUST cite every single factual sentence.

MANDATORY: Every sentence that makes a factual claim must end with at least one [SOURCE:chunk_id].
Use ONLY the provided context chunks.
If context is insufficient, respond: "The provided documents do not contain enough information to answer this question."
Do not speculate. Do not use knowledge outside the provided chunks."""


def build_user_prompt(question: str, chunks: list[tuple[str, str]], conversation_context: str) -> str:
    context_section = "\n\n".join(
        f"[CHUNK:{chunk_id}]\n{text}" for chunk_id, text in chunks
    )
    if conversation_context:
        return f"{conversation_context}\n\n[Retrieved context]\n{context_section}\n\n[Question]\n{question}"
    return f"[Retrieved context]\n{context_section}\n\n[Question]\n{question}"
