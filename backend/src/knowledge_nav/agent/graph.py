from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph

from knowledge_nav.agent import nodes
from knowledge_nav.agent.state import RAGState


def build_rag_graph() -> CompiledGraph:
    g: StateGraph = StateGraph(RAGState)

    g.add_node("analyse_query", nodes.analyse_query)
    g.add_node("hybrid_retrieve", nodes.hybrid_retrieve)
    g.add_node("rerank", nodes.rerank)
    g.add_node("inject_chat_history", nodes.inject_chat_history)
    g.add_node("generate", nodes.generate_with_citations)
    g.add_node("validate_citations", nodes.validate_citations)
    g.add_node("persist_message", nodes.persist_message)
    g.add_node("handle_error", nodes.handle_error)

    g.set_entry_point("analyse_query")
    g.add_edge("analyse_query", "hybrid_retrieve")
    g.add_edge("hybrid_retrieve", "rerank")
    g.add_edge("rerank", "inject_chat_history")
    g.add_edge("inject_chat_history", "generate")
    g.add_edge("generate", "validate_citations")
    g.add_conditional_edges(
        "validate_citations",
        nodes.citation_gate,
        {"pass": "persist_message", "retry": "generate", "fail": "handle_error"},
    )
    g.add_edge("persist_message", END)
    g.add_edge("handle_error", END)

    return g.compile()
