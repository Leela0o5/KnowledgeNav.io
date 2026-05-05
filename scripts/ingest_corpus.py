import argparse
import asyncio
from pathlib import Path

import chromadb

from src.config import settings
from ingestion.chunker import ChunkingConfig
from ingestion.embedder import build_embedder
from ingestion.indexer import ingest_corpus
from ingestion.loader import LOADER_REGISTRY


def _collect_input_paths(input_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for suffix in LOADER_REGISTRY:
        paths.extend(input_dir.glob(f"**/*{suffix}"))
    return paths


async def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into KnowledgeNav corpus")
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--corpus-id", required=True)
    parser.add_argument("--chunk-strategy", default="fixed", choices=["fixed"])
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    input_paths = _collect_input_paths(args.input_dir)
    if not input_paths:
        print(f"No supported files found in {args.input_dir}")
        return

    chroma_client = await chromadb.AsyncHttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    embedder = build_embedder()

    count = await ingest_corpus(
        input_paths=input_paths,
        corpus_id=args.corpus_id,
        chroma_client=chroma_client,
        embedder=embedder,
        bm25_index_dir=Path("/tmp/bm25_indices"),
        collection_prefix=settings.CHROMA_COLLECTION_PREFIX,
        chunking_config=ChunkingConfig(strategy=args.chunk_strategy),
        overwrite=args.overwrite,
    )
    print(f"Indexed {count} chunks for corpus '{args.corpus_id}'")


if __name__ == "__main__":
    asyncio.run(main())
