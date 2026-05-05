import uuid
from dataclasses import dataclass

import nltk  # type: ignore[import-untyped]

from ingestion.loader import Document
from retrieval.schema import Chunk


@dataclass(frozen=True)
class ChunkingConfig:
    strategy: str = "fixed"
    chunk_size: int = 512
    chunk_overlap: int = 50


def _fixed_chunk(text: str, chunk_size: int, overlap: int) -> list[str]:
    tokens = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunks.append(" ".join(tokens[start:end]))
        start += chunk_size - overlap
    return chunks


def chunk_documents(
    documents: list[Document],
    corpus_id: str,
    config: ChunkingConfig | None = None,
) -> list[Chunk]:
    if config is None:
        config = ChunkingConfig()
    chunks: list[Chunk] = []
    for doc_index, document in enumerate(documents):
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{corpus_id}:{document.source_file}:{doc_index}"))
        raw_chunks = _fixed_chunk(document.text, config.chunk_size, config.chunk_overlap)
        for chunk_index, chunk_text in enumerate(raw_chunks):
            if not chunk_text.strip():
                continue
            chunk_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}:{chunk_index}"))
            chunks.append(
                Chunk(
                    id=chunk_id,
                    text=chunk_text,
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                    source_file=document.source_file,
                    page_range=document.page_range,
                    corpus_id=corpus_id,
                )
            )
    return chunks
