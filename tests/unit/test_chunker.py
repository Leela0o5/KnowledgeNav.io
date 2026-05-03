from knowledge_nav.ingestion.chunker import ChunkingConfig, chunk_documents
from knowledge_nav.ingestion.loader import Document


def test_chunk_produces_chunks() -> None:
    docs = [Document(text="word " * 600, source_file="test.txt", page_range=None)]
    chunks = chunk_documents(docs, "test-corpus", ChunkingConfig(chunk_size=100, chunk_overlap=10))
    assert len(chunks) > 1
    assert all(c.corpus_id == "test-corpus" for c in chunks)


def test_chunk_ids_are_unique() -> None:
    docs = [Document(text="word " * 600, source_file="test.txt", page_range=None)]
    chunks = chunk_documents(docs, "test-corpus")
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids))


def test_empty_text_produces_no_chunks() -> None:
    docs = [Document(text="   ", source_file="test.txt", page_range=None)]
    chunks = chunk_documents(docs, "test-corpus")
    assert len(chunks) == 0
