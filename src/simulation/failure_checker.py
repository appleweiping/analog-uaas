from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List


@dataclass
class FailureCheckResult:
    simulation_failed: bool
    failure_reasons: List[str]
    metrics_complete: bool


class FailureChecker:
    REQUIRED_METRICS = ("gain_db", "gbw_hz", "pm_deg", "power_w")

    def check(
        self,
        runner_result: Dict[str, Any],
        metrics: Dict[str, float],
    ) -> FailureCheckResult:
        reasons: List[str] = []

        if not runner_result.get("success", False):
            reasons.append(runner_result.get("error_message", "runner marked failure"))

        metrics_path = Path(runner_result["metrics_path"])
        if not metrics_path.exists():
            reasons.append("metrics file missing")

        if metrics.get("simulation_failed", 0.0) == 1.0:
            reasons.append("simulation_failed flag found in metrics")

        missing = [m for m in self.REQUIRED_METRICS if m not in metrics]
        metrics_complete = len(missing) == 0
        if not metrics_complete:
            reasons.append(f"missing required metrics: {missing}")

        return FailureCheckResult(
            simulation_failed=(len(reasons) > 0),
            failure_reasons=reasons,
            metrics_complete=metrics_complete,
        )