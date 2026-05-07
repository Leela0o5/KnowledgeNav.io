import tempfile
from pathlib import Path

import pytest

from ingestion.loader import UnsupportedFileTypeError, load_document


def _write(suffix: str, content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, mode="w", encoding="utf-8", delete=False)
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


def test_load_text_file() -> None:
    path = _write(".txt", "Hello world")
    docs = load_document(path)
    assert len(docs) == 1
    assert "Hello world" in docs[0].text
    assert docs[0].page_range is None


def test_load_markdown_file() -> None:
    path = _write(".md", "# Title\n\nSome content.")
    docs = load_document(path)
    assert len(docs) == 1
    assert "Title" in docs[0].text


def test_unsupported_extension_raises() -> None:
    path = _write(".xyz", "data")
    with pytest.raises(UnsupportedFileTypeError) as exc_info:
        load_document(path)
    assert exc_info.value.suffix == ".xyz"


def test_source_file_is_set() -> None:
    path = _write(".txt", "content")
    docs = load_document(path)
    assert docs[0].source_file == str(path)
