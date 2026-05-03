import pytest

from knowledge_nav.citation.enforcer import CitationEnforcer


@pytest.fixture
def enforcer() -> CitationEnforcer:
    return CitationEnforcer(min_coverage=0.8)


def test_valid_answer_passes(enforcer: CitationEnforcer) -> None:
    answer = "The policy allows returns within 30 days. [SOURCE:chunk1] Refunds are processed in 5 business days. [SOURCE:chunk2]"
    result = enforcer.validate(answer, {"chunk1", "chunk2"})
    assert result.is_valid
    assert result.coverage >= 0.8


def test_hallucinated_id_fails(enforcer: CitationEnforcer) -> None:
    answer = "The policy allows returns within 30 days. [SOURCE:fake_chunk]"
    result = enforcer.validate(answer, {"chunk1"})
    assert not result.is_valid
    assert "fake_chunk" in result.hallucinated_ids


def test_low_coverage_fails(enforcer: CitationEnforcer) -> None:
    answer = "The policy allows returns within 30 days. Also refunds take 5 days. Also shipping is free. Also taxes apply."
    result = enforcer.validate(answer, {"chunk1"})
    assert not result.is_valid


def test_insufficient_context_response_passes(enforcer: CitationEnforcer) -> None:
    answer = "The provided documents do not contain enough information to answer this question."
    result = enforcer.validate(answer, set())
    assert result.is_valid
