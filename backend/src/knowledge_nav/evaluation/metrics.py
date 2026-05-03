from dataclasses import dataclass


@dataclass(frozen=True)
class MetricScore:
    name: str
    score: float
    threshold: float

    @property
    def passed(self) -> bool:
        return self.score >= self.threshold
