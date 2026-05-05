import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QAPair:
    question: str
    ground_truth: str
    reference_chunks: list[str]


def load_golden_dataset(path: Path) -> list[QAPair]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [
        QAPair(
            question=item["question"],
            ground_truth=item["ground_truth"],
            reference_chunks=item["reference_chunks"],
        )
        for item in raw
    ]
