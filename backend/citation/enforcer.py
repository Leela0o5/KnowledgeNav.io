import re

from citation.schema import CitationValidationResult

CITATION_PATTERN = re.compile(r"\[SOURCE:([a-zA-Z0-9_\-]+)\]")

_FACTUAL_EXCLUSIONS = re.compile(
    r"^(the provided documents do not|i cannot|i don't|based on the)",
    re.IGNORECASE,
)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _is_factual(sentence: str) -> bool:
    return not _FACTUAL_EXCLUSIONS.match(sentence)


def extract_citation_ids(text: str) -> set[str]:
    return set(CITATION_PATTERN.findall(text))


class CitationEnforcer:
    """Validates that LLM answers cite retrieved chunks and do not hallucinate citation IDs."""

    def __init__(self, min_coverage: float) -> None:
        self._min_coverage = min_coverage

    def validate(self, answer: str, valid_chunk_ids: set[str]) -> CitationValidationResult:
        sentences = _split_sentences(answer)
        factual = [s for s in sentences if _is_factual(s)]
        cited = [s for s in factual if CITATION_PATTERN.search(s)]
        coverage = len(cited) / len(factual) if factual else 1.0
        hallucinated = extract_citation_ids(answer) - valid_chunk_ids
        is_valid = coverage >= self._min_coverage and not hallucinated
        return CitationValidationResult(
            coverage=coverage,
            hallucinated_ids=hallucinated,
            is_valid=is_valid,
        )
