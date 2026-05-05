import functools
from pathlib import Path

import chromadb
import cohere
from langgraph.graph import END, StateGraph

from agent import nodes
from agent.state import RAGState
from ingestion.embedder import Embedder
from ingestion.indexer import load_bm25_retriever
from retrieval.reranker import CohereReranker
from retrieval.vector_retriever import VectorRetriever
from src.config import settings


async def build_rag_graph(corpus_id: str):
    bm25_retriever = load_bm25_retriever(corpus_id, Path("/tmp/bm25_indices"))

    cohere_client = cohere.AsyncClient(api_key=settings.COHERE_API_KEY)
    embedder = Embedder(client=cohere_client, model=settings.COHERE_EMBED_MODEL)

    chroma_client = await chromadb.AsyncHttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collection_name = f"{settings.CHROMA_COLLECTION_PREFIX}_{corpus_id}"
    collection = await chroma_client.get_collection(collection_name)
    vector_retriever = VectorRetriever(collection=collection, embedder=embedder)

    reranker = CohereReranker(
        client=cohere_client,
        model=settings.COHERE_RERANK_MODEL,
        top_n=settings.RERANK_TOP_N,
    )

    g: StateGraph = StateGraph(RAGState)
    g.add_node("analyse_query", nodes.analyse_query)
    g.add_node(
        "hybrid_retrieve",
        functools.partial(nodes.hybrid_retrieve, bm25_retrieve=bm25_retriever, vector_retrieve=vector_retriever),
    )
    g.add_node("rerank", functools.partial(nodes.rerank, reranker=reranker))
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
