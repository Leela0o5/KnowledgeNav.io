from knowledge_nav.retrieval.hybrid import reciprocal_rank_fusion
from knowledge_nav.retrieval.schema import Chunk, ScoredChunk


def _make_chunk(chunk_id: str) -> ScoredChunk:
    return ScoredChunk(
        chunk=Chunk(
            id=chunk_id,
            text="sample text",
            doc_id="doc1",
            chunk_index=0,
            source_file="file.txt",
            page_range=None,
            corpus_id="test",
        ),
        score=1.0,
    )


def test_rrf_merges_lists() -> None:
    a = [_make_chunk("c1"), _make_chunk("c2"), _make_chunk("c3")]
    b = [_make_chunk("c3"), _make_chunk("c1"), _make_chunk("c4")]
    result = reciprocal_rank_fusion(a, b, k=60)
    ids = [r.id for r in result]
    assert "c1" in ids
    assert "c3" in ids
    assert "c4" in ids
    assert ids[0] in ("c1", "c3")


def test_rrf_empty_lists() -> None:
    result = reciprocal_rank_fusion([], [], k=60)
    assert result == []


def test_rrf_one_empty_list() -> None:
    a = [_make_chunk("c1")]
    result = reciprocal_rank_fusion(a, [], k=60)
    assert len(result) == 1
    assert result[0].id == "c1"
