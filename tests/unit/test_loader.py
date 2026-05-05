import tempfile
from pathlib import Path

import pytest

from ingestion.loader import UnsupportedFileTypeError, load_document


def test_load_text_file() -> None:
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, encoding="utf-8") as f:
        f.write("Hello world. This is a test document.")
        tmp_path = Path(f.name)

    try:
        docs = load_document(tmp_path)
        assert len(docs) == 1
        assert "Hello world" in docs[0].text
    finally:
        tmp_path.unlink()


def test_load_markdown_file() -> None:
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False, encoding="utf-8") as f:
        f.write("# Title\n\nSome content here.")
        tmp_path = Path(f.name)

    try:
        docs = load_document(tmp_path)
        assert len(docs) == 1
        assert "Title" in docs[0].text
    finally:
        tmp_path.unlink()


def test_unsupported_extension_raises() -> None:
    with pytest.raises(UnsupportedFileTypeError):
        load_document(Path("file.xyz"))
