from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    doc_id: str
    chunk_index: int
    source_file: str
    page_range: str | None
    corpus_id: str


@dataclass(frozen=True)
class ScoredChunk:
    chunk: Chunk
    score: float

    @property
    def id(self) -> str:
        return self.chunk.id

    @property
    def text(self) -> str:
        return self.chunk.text
