from typing import Any

import chromadb

from knowledge_nav.ingestion.embedder import Embedder
from knowledge_nav.retrieval.schema import Chunk, ScoredChunk


def _parse_chroma_results(results: dict[str, Any]) -> list[ScoredChunk]:
    chunks: list[ScoredChunk] = []
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for chunk_id, text, meta, distance in zip(ids, documents, metadatas, distances):
        chunk = Chunk(
            id=chunk_id,
            text=text,
            doc_id=meta.get("doc_id", ""),
            chunk_index=int(meta.get("chunk_index", 0)),
            source_file=meta.get("source_file", ""),
            page_range=meta.get("page_range"),
            corpus_id=meta.get("corpus_id", ""),
        )
        similarity = 1.0 - float(distance)
        chunks.append(ScoredChunk(chunk=chunk, score=similarity))
    return chunks


class VectorRetriever:
    """Dense vector retriever backed by ChromaDB."""

    def __init__(self, collection: chromadb.Collection, embedder: Embedder) -> None:
        self._collection = collection
        self._embedder = embedder

    async def retrieve(self, query: str, top_k: int) -> list[ScoredChunk]:
        embedding = await self._embedder.embed_query(query)
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        return _parse_chroma_results(results)
