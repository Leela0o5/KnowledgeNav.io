from knowledge_nav.sessions.models import Message


def build_conversation_context(messages: list[Message]) -> str:
    return "\n".join(f"{m.role.upper()}: {m.content}" for m in messages)


def format_context_for_prompt(messages: list[Message], current_question: str) -> str:
    if not messages:
        return current_question
    context = build_conversation_context(messages)
    return f"[Previous conversation]\n{context}\n\n[Current question]\n{current_question}"
