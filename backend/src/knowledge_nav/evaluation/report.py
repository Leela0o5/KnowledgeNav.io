import json
from dataclasses import asdict, dataclass
from pathlib import Path

from knowledge_nav.evaluation.metrics import MetricScore


@dataclass
class EvalReport:
    scores: list[MetricScore]
    thresholds: dict[str, float]

    @property
    def passed(self) -> bool:
        return all(m.passed for m in self.scores)

    def save(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "passed": self.passed,
            "scores": [asdict(s) for s in self.scores],
        }
        with open(output_dir / "ragas_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def print_summary(self) -> None:
        for metric in self.scores:
            status = "PASS" if metric.passed else "FAIL"
            print(f"[{status}] {metric.name}: {metric.score:.4f} (threshold: {metric.threshold:.4f})")
