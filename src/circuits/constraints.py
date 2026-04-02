from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class SpecCheckResult:
    is_feasible: bool
    violations: Dict[str, float]
    margins: Dict[str, float]


def check_parameter_bounds(
    design: Dict[str, float],
    parameter_cfg: Dict[str, Any],
) -> List[str]:
    errors: List[str] = []
    for name, cfg in parameter_cfg.items():
        if name not in design:
            errors.append(f"missing parameter: {name}")
            continue
        value = float(design[name])
        low = float(cfg["low"])
        high = float(cfg["high"])
        if value < low or value > high:
            errors.append(f"{name} out of bounds: {value} not in [{low}, {high}]")
    return errors


def check_coupling_constraints(
    design: Dict[str, float],
    coupling_cfg: List[Dict[str, Any]],
) -> List[str]:
    errors: List[str] = []
    for rule in coupling_cfg:
        rule_type = str(rule["type"])
        num = str(rule["numerator"])
        den = str(rule["denominator"])
        value = float(rule["value"])
        if den not in design or num not in design:
            errors.append(f"missing keys for coupling constraint: {num}/{den}")
            continue
        ratio = float(design[num]) / max(float(design[den]), 1e-30)
        if rule_type == "ratio_min" and ratio < value:
            errors.append(f"{num}/{den}={ratio:.4g} < min {value}")
        elif rule_type == "ratio_max" and ratio > value:
            errors.append(f"{num}/{den}={ratio:.4g} > max {value}")
        else:
            if rule_type not in {"ratio_min", "ratio_max"}:
                errors.append(f"unknown coupling constraint type: {rule_type}")
    return errors


def evaluate_specs(
    metrics: Dict[str, float],
    constraint_cfg: Dict[str, float],
) -> SpecCheckResult:
    violations: Dict[str, float] = {}
    margins: Dict[str, float] = {}

    gain_db_min = float(constraint_cfg["gain_db_min"])
    gbw_hz_min = float(constraint_cfg["gbw_hz_min"])
    pm_deg_min = float(constraint_cfg["pm_deg_min"])
    power_w_max = float(constraint_cfg["power_w_max"])

    def require_min(metric_name: str, value: float, threshold: float) -> None:
        margin = value - threshold
        margins[metric_name] = margin
        if value < threshold:
            violations[metric_name] = threshold - value

    def require_max(metric_name: str, value: float, threshold: float) -> None:
        margin = threshold - value
        margins[metric_name] = margin
        if value > threshold:
            violations[metric_name] = value - threshold

    require_min("gain_db", float(metrics.get("gain_db", float("-inf"))), gain_db_min)
    require_min("gbw_hz", float(metrics.get("gbw_hz", float("-inf"))), gbw_hz_min)
    require_min("pm_deg", float(metrics.get("pm_deg", float("-inf"))), pm_deg_min)
    require_max("power_w", float(metrics.get("power_w", float("inf"))), power_w_max)

    return SpecCheckResult(
        is_feasible=(len(violations) == 0),
        violations=violations,
        margins=margins,
    )