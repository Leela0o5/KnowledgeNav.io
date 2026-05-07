import pickle
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import chromadb
from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

from auth.middleware import get_current_user
from auth.models import User
from retrieval.bm25_retriever import tokenize
from sessions.models import CorpusOwnership
from src.config import settings
from src.db import get_db

_BM25_DIR = Path("/tmp/bm25_indices")

router = APIRouter(prefix="/api/v1/corpora", tags=["corpora"])


class CorpusResponse(BaseModel):
    id: str
    name: str


class DocumentInfo(BaseModel):
    source_file: str
    chunk_count: int


async def _require_corpus_owner(
    corpus_id: str,
    current_user: User,
    db: AsyncSession,
) -> CorpusOwnership:
    ownership = await db.get(CorpusOwnership, corpus_id)
    if ownership is None or ownership.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corpus not found")
    return ownership


@router.get("", response_model=list[CorpusResponse])
async def list_corpora(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CorpusResponse]:
    result = await db.execute(
        select(CorpusOwnership).where(CorpusOwnership.user_id == current_user.id)
    )
    ownerships = result.scalars().all()
    return [CorpusResponse(id=o.corpus_id, name=o.name) for o in ownerships]


@router.get("/{corpus_id}/documents", response_model=list[DocumentInfo])
async def list_corpus_documents(
    corpus_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentInfo]:
    await _require_corpus_owner(corpus_id, current_user, db)

    chroma_client = await chromadb.AsyncHttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collection_name = f"{settings.CHROMA_COLLECTION_PREFIX}_{corpus_id}"
    try:
        collection = await chroma_client.get_collection(collection_name)
        results = await collection.get(include=["metadatas"])
        metadatas = results.get("metadatas") or []
        counts: dict[str, int] = {}
        for meta in metadatas:
            src = (meta or {}).get("source_file", "unknown")
            counts[src] = counts.get(src, 0) + 1
        return [
            DocumentInfo(source_file=k, chunk_count=v)
            for k, v in sorted(counts.items())
        ]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corpus not found")


@router.delete("/{corpus_id}/documents", status_code=status.HTTP_204_NO_CONTENT)
async def delete_corpus_document(
    corpus_id: str,
    source_file: str = Query(..., description="Exact source_file value stored in chunk metadata"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await _require_corpus_owner(corpus_id, current_user, db)

    chroma_client = await chromadb.AsyncHttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collection_name = f"{settings.CHROMA_COLLECTION_PREFIX}_{corpus_id}"
    try:
        collection = await chroma_client.get_collection(collection_name)
        await collection.delete(where={"source_file": source_file})
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corpus not found")

    bm25_path = _BM25_DIR / f"{corpus_id}_bm25.pkl"
    if bm25_path.exists():
        with open(bm25_path, "rb") as f:
            data = pickle.load(f)
        remaining = [c for c in data["chunks"] if c.source_file != source_file]
        if remaining:
            new_index = BM25Okapi([tokenize(c.text) for c in remaining])
            with open(bm25_path, "wb") as f:
                pickle.dump({"index": new_index, "chunks": remaining}, f)
        else:
            bm25_path.unlink(missing_ok=True)


@router.delete("/{corpus_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_corpus(
    corpus_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    ownership = await _require_corpus_owner(corpus_id, current_user, db)

    chroma_client = await chromadb.AsyncHttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collection_name = f"{settings.CHROMA_COLLECTION_PREFIX}_{corpus_id}"
    try:
        await chroma_client.delete_collection(collection_name)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corpus not found")

    await db.delete(ownership)
    await db.commit()

    bm25_path = _BM25_DIR / f"{corpus_id}_bm25.pkl"
    bm25_path.unlink(missing_ok=True)
