from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class SampleRecord:
    sample_id: str

    # raw design-side information
    x_raw: Dict[str, float]
    x_norm: Optional[Dict[str, float]] = None
    environment: Dict[str, Any] = field(default_factory=dict)

    # raw response-side information
    y: Dict[str, float] = field(default_factory=dict)
    y_norm: Optional[Dict[str, float]] = None

    # spec / constraint semantics
    is_feasible: bool = False
    overall_spec_satisfied: bool = False
    constraint_satisfaction: Dict[str, bool] = field(default_factory=dict)
    constraint_violation: Dict[str, float] = field(default_factory=dict)
    constraint_margin: Dict[str, float] = field(default_factory=dict)
    nearest_constraint: Optional[str] = None
    boundary_distance: Optional[float] = None
    boundary_label: Optional[str] = None  # safe / boundary / infeasible / failed

    # execution status
    simulation_success: bool = False
    simulation_failed: bool = False
    failure_type: Optional[str] = None
    failure_reasons: List[str] = field(default_factory=list)
    metrics_complete: bool = True
    simulation_time_sec: Optional[float] = None

    # provenance
    source_stage: Optional[str] = None
    seed: Optional[int] = None
    dataset_version: Optional[str] = None
    config_name: Optional[str] = None
    run_id: Optional[str] = None
    split: Optional[str] = None

    # metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SampleRecord":
        return cls(**payload)