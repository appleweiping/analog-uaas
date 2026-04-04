from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from src.data.schema import SampleRecord
from src.utils.io import dump_json, load_json


@dataclass
class AnalogDataset:
    records: List[SampleRecord]

    @classmethod
    def from_json(cls, path: str | Path) -> "AnalogDataset":
        raw = load_json(path)
        return cls(records=[SampleRecord.from_dict(item) for item in raw])

    def to_json(self, path: str | Path) -> None:
        dump_json([record.to_dict() for record in self.records], path)

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> SampleRecord:
        return self.records[idx]

    def to_dicts(self) -> List[Dict[str, Any]]:
        return [record.to_dict() for record in self.records]

    def select(self, split: str) -> "AnalogDataset":
        return AnalogDataset([record for record in self.records if record.split == split])

    def filter_failed(self, keep_failed: bool = False) -> "AnalogDataset":
        if keep_failed:
            return AnalogDataset(list(self.records))
        return AnalogDataset([r for r in self.records if not r.simulation_failed])

    def feature_rows(self, normalized: bool = False) -> List[Dict[str, float]]:
        rows: List[Dict[str, float]] = []
        for record in self.records:
            if normalized and record.x_norm is not None:
                rows.append(record.x_norm)
            else:
                rows.append(record.x_raw)
        return rows

    def target_rows(self, normalized: bool = False) -> List[Dict[str, float]]:
        rows: List[Dict[str, float]] = []
        for record in self.records:
            if normalized and record.y_norm is not None:
                rows.append(record.y_norm)
            else:
                rows.append(record.y)
        return rows

    def summary(self) -> Dict[str, Any]:
        total = len(self.records)
        failed = sum(1 for r in self.records if r.simulation_failed)
        feasible = sum(1 for r in self.records if r.is_feasible)
        by_label: Dict[str, int] = {}
        for record in self.records:
            key = record.boundary_label or "unknown"
            by_label[key] = by_label.get(key, 0) + 1
        return {
            "total": total,
            "failed": failed,
            "feasible": feasible,
            "feasible_ratio": feasible / total if total else 0.0,
            "failure_ratio": failed / total if total else 0.0,
            "boundary_label_counts": by_label,
        }