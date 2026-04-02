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

    def __init__(self, require_metrics_file_exists: bool = True) -> None:
        """
        require_metrics_file_exists:
            True  -> 真实运行（严格）
            False -> 测试模式（不依赖文件）
        """
        self.require_metrics_file_exists = require_metrics_file_exists

    def check(
        self,
        runner_result: Dict[str, Any],
        metrics: Dict[str, float],
    ) -> FailureCheckResult:

        reasons: List[str] = []

        # ---------------------------
        # 1️⃣ 仿真执行失败
        # ---------------------------
        if not runner_result.get("success", False):
            reasons.append("simulation_error")

        # ---------------------------
        # 2️⃣ metrics 文件检查（可选）
        # ---------------------------
        metrics_path = runner_result.get("metrics_path", "")
        if self.require_metrics_file_exists:
            if not Path(metrics_path).exists():
                reasons.append("metrics_file_missing")

        # ---------------------------
        # 3️⃣ metrics 内容完整性
        # ---------------------------
        missing_metrics = [
            m for m in self.REQUIRED_METRICS if m not in metrics
        ]

        metrics_complete = len(missing_metrics) == 0

        if not metrics_complete:
            reasons.append(f"metrics_missing:{missing_metrics}")

        # ---------------------------
        # 4️⃣ 特殊标记（mock / real）
        # ---------------------------
        if metrics.get("simulation_failed", 0.0) == 1.0:
            reasons.append("simulation_flagged_failure")

        # ---------------------------
        # 最终判定
        # ---------------------------
        simulation_failed = len(reasons) > 0

        return FailureCheckResult(
            simulation_failed=simulation_failed,
            failure_reasons=reasons,
            metrics_complete=metrics_complete,
        )