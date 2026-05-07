import pickle
from pathlib import Path

import chromadb
from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

from ingestion.embedder import Embedder
from ingestion.loader import Document, load_document
from ingestion.chunker import ChunkingConfig, chunk_documents
from retrieval.bm25_retriever import BM25Retriever, tokenize
from retrieval.schema import Chunk
from retrieval.vector_retriever import VectorRetriever


_BATCH_SIZE = 64


async def ingest_corpus(
    input_paths: list[Path],
    corpus_id: str,
    chroma_client: chromadb.AsyncClientAPI,
    embedder: Embedder,
    bm25_index_dir: Path,
    collection_prefix: str,
    chunking_config: ChunkingConfig | None = None,
    overwrite: bool = False,
) -> int:
    documents: list[Document] = []
    for path in input_paths:
        documents.extend(load_document(path))

    chunks = chunk_documents(documents, corpus_id, chunking_config)
    collection_name = f"{collection_prefix}_{corpus_id}"

    if overwrite:
        try:
            await chroma_client.delete_collection(collection_name)
        except Exception:
            pass

    collection = await chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    for i in range(0, len(chunks), _BATCH_SIZE):
        batch = chunks[i : i + _BATCH_SIZE]
        texts = [c.text for c in batch]
        embeddings = await embedder.embed_documents(texts)
        await collection.upsert(
            ids=[c.id for c in batch],
            embeddings=embeddings,
            documents=texts,
            metadatas=[
                {
                    "doc_id": c.doc_id,
                    "chunk_index": c.chunk_index,
                    "source_file": c.source_file,
                    "page_range": c.page_range or "",
                    "corpus_id": c.corpus_id,
                }
                for c in batch
            ],
        )

    bm25_index_dir.mkdir(parents=True, exist_ok=True)
    tokenized_corpus = [tokenize(c.text) for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    index_path = bm25_index_dir / f"{corpus_id}_bm25.pkl"
    with open(index_path, "wb") as f:
        pickle.dump({"index": bm25, "chunks": chunks}, f)

    return len(chunks)


def load_bm25_retriever(corpus_id: str, bm25_index_dir: Path) -> BM25Retriever:
    index_path = bm25_index_dir / f"{corpus_id}_bm25.pkl"
    with open(index_path, "rb") as f:
        data = pickle.load(f)
    return BM25Retriever(index=data["index"], chunks=data["chunks"])
