from citation.enforcer import CitationEnforcer, extract_citation_ids
from citation.schema import CitationValidationResult


VALID_IDS = {"chunk-1", "chunk-2", "chunk-3"}


def test_valid_answer_passes() -> None:
    enforcer = CitationEnforcer(min_coverage=0.8)
    answer = (
        "The sky is blue [SOURCE:chunk-1]. "
        "Water is wet [SOURCE:chunk-2]. "
        "Fire is hot [SOURCE:chunk-3]."
    )
    result = enforcer.validate(answer, VALID_IDS)
    assert result.is_valid
    assert result.coverage >= 0.8
    assert not result.hallucinated_ids


def test_hallucinated_id_fails() -> None:
    enforcer = CitationEnforcer(min_coverage=0.5)
    answer = "The sky is blue. [SOURCE:fake-id]"
    result = enforcer.validate(answer, VALID_IDS)
    assert not result.is_valid
    assert "fake-id" in result.hallucinated_ids


def test_low_coverage_fails() -> None:
    enforcer = CitationEnforcer(min_coverage=0.8)
    answer = (
        "The sky is blue. "
        "Water is wet. "
        "Fire is hot. [SOURCE:chunk-1]"
    )
    result = enforcer.validate(answer, VALID_IDS)
    assert not result.is_valid
    assert result.coverage < 0.8


def test_extract_citation_ids() -> None:
    ids = extract_citation_ids("See [SOURCE:abc] and [SOURCE:def].")
    assert ids == {"abc", "def"}


def test_no_citations_no_hallucinations() -> None:
    enforcer = CitationEnforcer(min_coverage=0.0)
    result = enforcer.validate("Plain answer with no citations.", set())
    assert not result.hallucinated_ids


def test_citation_validation_result_fields() -> None:
    r = CitationValidationResult(coverage=0.9, hallucinated_ids=set(), is_valid=True)
    assert r.coverage == 0.9
    assert r.is_valid
