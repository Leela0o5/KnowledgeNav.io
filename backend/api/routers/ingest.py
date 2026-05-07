import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth.middleware import get_current_user
from auth.models import User
from sessions.models import CorpusOwnership
from src.config import settings
from src.db import get_db
from ingestion.chunker import ChunkingConfig
from ingestion.embedder import build_embedder
from ingestion.indexer import ingest_corpus

router = APIRouter(prefix="/api/v1", tags=["ingest"])


class IngestResponse(BaseModel):
    corpus_id: str
    chunks_indexed: int


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest(
    corpus_id: str = Form(...),
    overwrite: bool = Form(False),
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    import chromadb

    existing = await db.get(CorpusOwnership, corpus_id)
    if existing is not None and existing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Corpus belongs to another user",
        )

    chroma_client = await chromadb.AsyncHttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    embedder = build_embedder()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_paths: list[Path] = []
        for upload in files:
            if upload.filename is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File missing filename")
            dest = tmp_path / upload.filename
            dest.write_bytes(await upload.read())
            input_paths.append(dest)

        count = await ingest_corpus(
            input_paths=input_paths,
            corpus_id=corpus_id,
            chroma_client=chroma_client,
            embedder=embedder,
            bm25_index_dir=Path("/tmp/bm25_indices"),
            collection_prefix=settings.CHROMA_COLLECTION_PREFIX,
            chunking_config=ChunkingConfig(),
            overwrite=overwrite,
        )

    if existing is None:
        db.add(CorpusOwnership(
            corpus_id=corpus_id,
            user_id=current_user.id,
            name=corpus_id,
            created_at=datetime.now(timezone.utc),
        ))
        await db.commit()

    return IngestResponse(corpus_id=corpus_id, chunks_indexed=count)
