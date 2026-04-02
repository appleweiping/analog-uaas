from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Any


class ResultParser:
    def __init__(self) -> None:
        self.kv_pattern = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*([-+eE0-9\.]+)\s*$")

        self.fallback_patterns = {
            "gain_db": re.compile(r"gain[_\s-]*db\s*[:=]\s*([-+eE0-9\.]+)", re.IGNORECASE),
            "gbw_hz": re.compile(r"gbw[_\s-]*hz\s*[:=]\s*([-+eE0-9\.]+)", re.IGNORECASE),
            "pm_deg": re.compile(r"(pm|phase[_\s-]*margin)[_\s-]*(deg)?\s*[:=]\s*([-+eE0-9\.]+)", re.IGNORECASE),
            "power_w": re.compile(r"power[_\s-]*w\s*[:=]\s*([-+eE0-9\.]+)", re.IGNORECASE),
        }

    def parse_metrics_file(self, metrics_path: str | Path) -> Dict[str, float]:
        metrics_path = Path(metrics_path)
        if not metrics_path.exists():
            return {}

        metrics: Dict[str, float] = {}
        for line in metrics_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = self.kv_pattern.match(line.strip())
            if not m:
                continue
            key, value = m.group(1), m.group(2)
            try:
                metrics[key] = float(value)
            except ValueError:
                continue
        return metrics

    def parse_log_fallback(self, log_path: str | Path) -> Dict[str, float]:
        log_path = Path(log_path)
        if not log_path.exists():
            return {}

        text = log_path.read_text(encoding="utf-8", errors="ignore")
        metrics: Dict[str, float] = {}

        for key, pattern in self.fallback_patterns.items():
            m = pattern.search(text)
            if not m:
                continue
            # pm pattern has different groups
            if key == "pm_deg":
                value_str = m.group(3)
            else:
                value_str = m.group(1)
            try:
                metrics[key] = float(value_str)
            except ValueError:
                pass
        return metrics

    def parse(self, metrics_path: str | Path, log_path: str | Path | None = None) -> Dict[str, float]:
        metrics = self.parse_metrics_file(metrics_path)
        if metrics:
            return metrics

        if log_path is not None:
            return self.parse_log_fallback(log_path)

        return {}