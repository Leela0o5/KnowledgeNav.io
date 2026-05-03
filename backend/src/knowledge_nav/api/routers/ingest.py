import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from knowledge_nav.auth.middleware import require_corpus_admin
from knowledge_nav.auth.models import User
from knowledge_nav.config import settings
from knowledge_nav.ingestion.chunker import ChunkingConfig
from knowledge_nav.ingestion.embedder import build_embedder
from knowledge_nav.ingestion.indexer import ingest_corpus

router = APIRouter(prefix="/api/v1", tags=["ingest"])


class IngestResponse(BaseModel):
    corpus_id: str
    chunks_indexed: int


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest(
    corpus_id: str = Form(...),
    overwrite: bool = Form(False),
    files: list[UploadFile] = File(...),
    current_user: User = Depends(require_corpus_admin),
) -> IngestResponse:
    import chromadb

    chroma_client = chromadb.AsyncHttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
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
