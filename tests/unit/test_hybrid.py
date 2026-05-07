from retrieval.hybrid import reciprocal_rank_fusion
from retrieval.schema import Chunk, ScoredChunk


def _sc(id: str, score: float = 1.0) -> ScoredChunk:
    chunk = Chunk(
        id=id,
        text="text",
        doc_id="doc",
        chunk_index=0,
        source_file="f.txt",
        page_range=None,
        corpus_id="c",
    )
    return ScoredChunk(chunk=chunk, score=score)


def test_rrf_merges_lists() -> None:
    result = reciprocal_rank_fusion([_sc("x"), _sc("y")], [_sc("y"), _sc("z")], k=60)
    assert {r.id for r in result} == {"x", "y", "z"}


def test_rrf_empty_lists() -> None:
    assert reciprocal_rank_fusion([], [], k=60) == []


def test_rrf_one_empty_list() -> None:
    result = reciprocal_rank_fusion([_sc("a"), _sc("b")], [], k=60)
    assert len(result) == 2
    assert result[0].id == "a"


def test_rrf_prefers_top_ranked_in_both_lists() -> None:
    shared = _sc("top")
    result = reciprocal_rank_fusion(
        [shared, _sc("only-a")], [shared, _sc("only-b")], k=60
    )
    assert result[0].id == "top"
