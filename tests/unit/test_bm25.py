from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

from knowledge_nav.retrieval.bm25_retriever import BM25Retriever, tokenize
from knowledge_nav.retrieval.schema import Chunk


def _make_retriever() -> BM25Retriever:
    texts = [
        "the cat sat on the mat",
        "the dog ran in the park",
        "machine learning is a subset of artificial intelligence",
    ]
    chunks = [
        Chunk(id=f"c{i}", text=t, doc_id="doc1", chunk_index=i, source_file="f.txt", page_range=None, corpus_id="test")
        for i, t in enumerate(texts)
    ]
    index = BM25Okapi([tokenize(t) for t in texts])
    return BM25Retriever(index=index, chunks=chunks)


def test_retrieve_returns_top_k() -> None:
    retriever = _make_retriever()
    results = retriever.retrieve("cat mat", top_k=2)
    assert len(results) == 2


def test_retrieve_most_relevant_first() -> None:
    retriever = _make_retriever()
    results = retriever.retrieve("machine learning artificial intelligence", top_k=3)
    assert results[0].id == "c2"
