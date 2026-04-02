from __future__ import annotations

import math
import random
from typing import Dict, Any, List

from src.circuits.base_circuit import BaseCircuit
from src.circuits.constraints import (
    check_parameter_bounds,
    check_coupling_constraints,
)


class TwoStageOpAmpCircuit(BaseCircuit):
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(name=config["name"], config=config)
        self.design_cfg = config["design_space"]
        self.env_cfg = config["environment"]

    def _sample_one_param(self, rng: random.Random, name: str, cfg: Dict[str, Any]) -> float:
        low = float(cfg["low"])
        high = float(cfg["high"])
        scale = str(cfg.get("scale", "linear")).lower()

        if low <= 0 and scale == "log":
            raise ValueError(f"{name}: log scale requires low > 0, got {low}")
        if high <= low:
            raise ValueError(f"{name}: invalid range, low={low}, high={high}")

        if scale == "linear":
            return rng.uniform(low, high)
        if scale == "log":
            return math.exp(rng.uniform(math.log(low), math.log(high)))

        raise ValueError(f"unknown scale for {name}: {scale}")

    def sample_design(self, rng: random.Random) -> Dict[str, float]:
        params_cfg = self.design_cfg["parameters"]

        max_trials = 500
        for _ in range(max_trials):
            design = {
                name: self._sample_one_param(rng, name, cfg)
                for name, cfg in params_cfg.items()
            }
            ok, _ = self.validate_design(design)
            if ok:
                return design
        raise RuntimeError("failed to sample a valid design after many trials")

    def sample_designs(self, n: int, seed: int | None = None) -> List[Dict[str, float]]:
        rng = random.Random(seed)
        return [self.sample_design(rng) for _ in range(n)]

    def validate_design(self, design: Dict[str, float]) -> tuple[bool, List[str]]:
        params_cfg = self.design_cfg["parameters"]
        coupling_cfg = self.design_cfg.get("coupling_constraints", [])

        errors = []
        errors.extend(check_parameter_bounds(design, params_cfg))
        errors.extend(check_coupling_constraints(design, coupling_cfg))
        return (len(errors) == 0, errors)

    def to_netlist_params(self, design: Dict[str, float]) -> Dict[str, Any]:
        params = dict(design)
        params.update(self.env_cfg)
        return params