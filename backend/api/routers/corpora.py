from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

import chromadb

from auth.middleware import get_current_user
from auth.models import User
from src.config import settings

router = APIRouter(prefix="/api/v1/corpora", tags=["corpora"])


class CorpusResponse(BaseModel):
    id: str
    name: str


@router.get("", response_model=list[CorpusResponse])
async def list_corpora(current_user: User = Depends(get_current_user)) -> list[CorpusResponse]:
    chroma_client = await chromadb.AsyncHttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collections = await chroma_client.list_collections()
    prefix = settings.CHROMA_COLLECTION_PREFIX + "_"
    result = []
    for col in collections:
        name = col.name if hasattr(col, "name") else str(col)
        if name.startswith(prefix):
            corpus_id = name[len(prefix):]
            result.append(CorpusResponse(id=corpus_id, name=corpus_id))
    return result


@router.delete("/{corpus_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_corpus(
    corpus_id: str,
    current_user: User = Depends(get_current_user),
) -> None:
    chroma_client = await chromadb.AsyncHttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collection_name = f"{settings.CHROMA_COLLECTION_PREFIX}_{corpus_id}"
    try:
        await chroma_client.delete_collection(collection_name)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corpus not found")
