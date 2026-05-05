import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from auth.middleware import get_current_user
from auth.models import User
from src.config import settings
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
) -> IngestResponse:
    import chromadb

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

    return IngestResponse(corpus_id=corpus_id, chunks_indexed=count)
