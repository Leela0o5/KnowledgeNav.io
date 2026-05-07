import asyncio
from pathlib import Path

import pytest

from evaluation.dataset import load_golden_dataset
from evaluation.pipeline import run_ragas_evaluation

@pytest.mark.skipif(
    not Path("tests/eval/golden_dataset.json").exists(),
    reason="Golden dataset not found",
)
def test_ragas_thresholds_pass() -> None:
    dataset = load_golden_dataset(Path("tests/eval/golden_dataset.json"))
    report = asyncio.run(run_ragas_evaluation(dataset, "ci-eval"))
    report.print_summary()
    assert report.passed, "One or more Ragas metrics are below threshold"
