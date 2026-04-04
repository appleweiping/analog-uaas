from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass
class FeatureStats:
    mean: float
    std: float
    min: float
    max: float
    count: int


@dataclass
class StandardNormalizer:
    stats: Dict[str, FeatureStats] = field(default_factory=dict)
    eps: float = 1e-12

    def fit(self, rows: Iterable[Dict[str, float]]) -> "StandardNormalizer":
        rows = list(rows)
        if not rows:
            raise ValueError("cannot fit normalizer on empty rows")

        keys = sorted(rows[0].keys())
        accum: Dict[str, List[float]] = {k: [] for k in keys}
        for row in rows:
            for key in keys:
                accum[key].append(float(row[key]))

        fitted: Dict[str, FeatureStats] = {}
        for key, values in accum.items():
            n = len(values)
            mean = sum(values) / n
            var = sum((v - mean) ** 2 for v in values) / max(n, 1)
            std = var ** 0.5
            fitted[key] = FeatureStats(
                mean=mean,
                std=max(std, self.eps),
                min=min(values),
                max=max(values),
                count=n,
            )
        self.stats = fitted
        return self

    def transform_row(self, row: Dict[str, float]) -> Dict[str, float]:
        if not self.stats:
            raise ValueError("normalizer is not fitted")
        return {
            key: (float(row[key]) - self.stats[key].mean) / self.stats[key].std
            for key in self.stats.keys()
        }

    def inverse_transform_row(self, row: Dict[str, float]) -> Dict[str, float]:
        if not self.stats:
            raise ValueError("normalizer is not fitted")
        return {
            key: float(row[key]) * self.stats[key].std + self.stats[key].mean
            for key in self.stats.keys()
        }

    def transform(self, rows: Iterable[Dict[str, float]]) -> List[Dict[str, float]]:
        return [self.transform_row(row) for row in rows]

    def to_dict(self) -> Dict[str, Dict[str, float]]:
        return {
            key: {
                "mean": value.mean,
                "std": value.std,
                "min": value.min,
                "max": value.max,
                "count": value.count,
            }
            for key, value in self.stats.items()
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Dict[str, float]]) -> "StandardNormalizer":
        obj = cls()
        obj.stats = {
            key: FeatureStats(
                mean=float(value["mean"]),
                std=float(value["std"]),
                min=float(value["min"]),
                max=float(value["max"]),
                count=int(value["count"]),
            )
            for key, value in payload.items()
        }
        return obj