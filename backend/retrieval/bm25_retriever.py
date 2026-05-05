import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

from retrieval.schema import Chunk, ScoredChunk


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


class BM25Retriever:
    """Keyword-based retriever using BM25Okapi over the corpus chunks."""

    def __init__(self, index: BM25Okapi, chunks: list[Chunk]) -> None:
        self._index = index
        self._chunks = chunks

    def retrieve(self, query: str, top_k: int) -> list[ScoredChunk]:
        scores = self._index.get_scores(tokenize(query))
        top_indices = scores.argsort()[-top_k:][::-1]
        return [
            ScoredChunk(chunk=self._chunks[int(i)], score=float(scores[int(i)]))
            for i in top_indices
        ]
