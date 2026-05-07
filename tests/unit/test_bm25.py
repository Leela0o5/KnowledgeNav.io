from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

from retrieval.bm25_retriever import BM25Retriever, tokenize
from retrieval.schema import Chunk, ScoredChunk


def _chunk(id: str, text: str) -> Chunk:
    return Chunk(
        id=id,
        text=text,
        doc_id="doc1",
        chunk_index=0,
        source_file="file.txt",
        page_range=None,
        corpus_id="test-corpus",
    )


def _build_retriever(texts: dict[str, str]) -> BM25Retriever:
    chunks = [_chunk(cid, text) for cid, text in texts.items()]
    index = BM25Okapi([tokenize(c.text) for c in chunks])
    return BM25Retriever(index=index, chunks=chunks)


def test_retrieve_returns_top_k() -> None:
    retriever = _build_retriever({f"c{i}": f"word{i} content" for i in range(5)})
    results = retriever.retrieve("word0 content", top_k=2)
    assert len(results) == 2


def test_retrieve_most_relevant_first() -> None:
    retriever = _build_retriever(
        {
            "a": "machine learning neural network",
            "b": "cooking recipes pasta dinner",
            "c": "machine learning deep learning",
        }
    )
    results = retriever.retrieve("machine learning", top_k=3)
    ids = [r.chunk.id for r in results]
    assert ids[-1] == "b"
    assert ids[0] in {"a", "c"}


def test_tokenize_lowercases_and_splits() -> None:
    tokens = tokenize("Hello World FOO")
    assert tokens == ["hello", "world", "foo"]


def test_scored_chunk_properties() -> None:
    chunk = _chunk("x", "sample text")
    sc = ScoredChunk(chunk=chunk, score=0.9)
    assert sc.id == "x"
    assert sc.text == "sample text"
