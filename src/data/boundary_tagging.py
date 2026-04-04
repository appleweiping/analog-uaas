from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional


@dataclass
class BoundaryTagResult:
    label: str
    boundary_distance: Optional[float]
    nearest_constraint: Optional[str]
    constraint_satisfaction: Dict[str, bool]
    constraint_violation: Dict[str, float]
    constraint_margin: Dict[str, float]


class BoundaryTagger:
    def __init__(self, boundary_epsilon: float = 0.10) -> None:
        if boundary_epsilon < 0.0:
            raise ValueError("boundary_epsilon must be non-negative")
        self.boundary_epsilon = float(boundary_epsilon)

    def tag(
        self,
        margins: Dict[str, float],
        simulation_failed: bool = False,
        failure_reasons: Optional[Iterable[str]] = None,
    ) -> BoundaryTagResult:
        margins = {str(k): float(v) for k, v in margins.items()}
        failure_reasons = list(failure_reasons or [])

        if simulation_failed:
            return BoundaryTagResult(
                label="failed",
                boundary_distance=None,
                nearest_constraint=None,
                constraint_satisfaction={k: False for k in margins},
                constraint_violation={k: 0.0 for k in margins},
                constraint_margin=margins,
            )

        if not margins:
            raise ValueError("margins cannot be empty when simulation_failed is False")

        nearest_constraint = min(margins, key=lambda k: margins[k])
        boundary_distance = float(margins[nearest_constraint])
        constraint_satisfaction = {k: (v >= 0.0) for k, v in margins.items()}
        constraint_violation = {k: max(0.0, -float(v)) for k, v in margins.items()}
        is_feasible = all(constraint_satisfaction.values())

        if not is_feasible:
            label = "infeasible"
        elif boundary_distance <= self.boundary_epsilon:
            label = "boundary"
        else:
            label = "safe"

        return BoundaryTagResult(
            label=label,
            boundary_distance=boundary_distance,
            nearest_constraint=nearest_constraint,
            constraint_satisfaction=constraint_satisfaction,
            constraint_violation=constraint_violation,
            constraint_margin=margins,
        )