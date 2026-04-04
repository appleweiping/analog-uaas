from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence


@dataclass
class SplitIndices:
    train: List[int]
    val: List[int]
    test: List[int]

    def to_dict(self) -> Dict[str, List[int]]:
        return {"train": self.train, "val": self.val, "test": self.test}


@dataclass
class SplitConfig:
    train_ratio: float = 0.70
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    seed: int = 42

    def validate(self) -> None:
        total = self.train_ratio + self.val_ratio + self.test_ratio
        if abs(total - 1.0) > 1e-8:
            raise ValueError(f"split ratios must sum to 1.0, got {total}")


class DatasetSplitter:
    def __init__(self, config: SplitConfig) -> None:
        config.validate()
        self.config = config

    def split_indices(self, n: int) -> SplitIndices:
        if n <= 0:
            raise ValueError("n must be positive")
        rng = random.Random(self.config.seed)
        indices = list(range(n))
        rng.shuffle(indices)

        n_train = int(round(n * self.config.train_ratio))
        n_val = int(round(n * self.config.val_ratio))
        n_train = min(n_train, n)
        n_val = min(n_val, n - n_train)
        n_test = n - n_train - n_val

        train = sorted(indices[:n_train])
        val = sorted(indices[n_train:n_train + n_val])
        test = sorted(indices[n_train + n_val:n_train + n_val + n_test])
        return SplitIndices(train=train, val=val, test=test)

    def split_records(self, records: Sequence[dict]) -> Dict[str, List[dict]]:
        splits = self.split_indices(len(records))
        return {
            "train": [records[i] for i in splits.train],
            "val": [records[i] for i in splits.val],
            "test": [records[i] for i in splits.test],
        }