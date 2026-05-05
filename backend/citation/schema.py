from dataclasses import dataclass, field


@dataclass(frozen=True)
class Citation:
    chunk_id: str
    source_file: str
    page_range: str | None
    excerpt: str


@dataclass(frozen=True)
class AnswerWithCitations:
    content: str
    citations: list[Citation]
    citation_coverage: float
    is_valid: bool
    warning: str | None = None


@dataclass(frozen=True)
class CitationValidationResult:
    coverage: float
    hallucinated_ids: set[str]
    is_valid: bool
