from ingestion.chunker import ChunkingConfig, chunk_documents
from ingestion.loader import Document


def _doc(text: str) -> Document:
    return Document(text=text, source_file="test.txt", page_range=None)


def test_chunk_produces_chunks() -> None:
    doc = _doc(" ".join(["word"] * 600))
    chunks = chunk_documents([doc], "corpus1")
    assert len(chunks) >= 2


def test_chunk_ids_are_unique() -> None:
    doc = _doc(" ".join(["word"] * 600))
    chunks = chunk_documents([doc], "corpus1")
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids))


def test_empty_text_produces_no_chunks() -> None:
    doc = _doc("   ")
    assert chunk_documents([doc], "corpus1") == []


def test_chunk_carries_corpus_id() -> None:
    doc = _doc("hello world")
    chunks = chunk_documents([doc], "my-corpus")
    assert all(c.corpus_id == "my-corpus" for c in chunks)


def test_custom_chunk_size() -> None:
    doc = _doc(" ".join(["word"] * 200))
    config = ChunkingConfig(chunk_size=100, chunk_overlap=0)
    chunks = chunk_documents([doc], "c", config)
    assert len(chunks) == 2


def test_multiple_documents() -> None:
    docs = [_doc("alpha beta"), _doc("gamma delta")]
    chunks = chunk_documents(docs, "multi")
    assert len(chunks) == 2
    sources = {c.source_file for c in chunks}
    assert sources == {"test.txt"}
