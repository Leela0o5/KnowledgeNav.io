from collections import defaultdict

from knowledge_nav.retrieval.schema import ScoredChunk


def reciprocal_rank_fusion(
    results_a: list[ScoredChunk],
    results_b: list[ScoredChunk],
    k: int,
) -> list[ScoredChunk]:
    """Merge two ranked lists using RRF. Higher k reduces the impact of rank differences."""
    scores: dict[str, float] = defaultdict(float)
    chunk_map: dict[str, ScoredChunk] = {}

    for rank, chunk in enumerate(results_a):
        scores[chunk.id] += 1.0 / (k + rank + 1)
        chunk_map[chunk.id] = chunk

    for rank, chunk in enumerate(results_b):
        scores[chunk.id] += 1.0 / (k + rank + 1)
        chunk_map[chunk.id] = chunk

    return sorted(chunk_map.values(), key=lambda c: scores[c.id], reverse=True)
