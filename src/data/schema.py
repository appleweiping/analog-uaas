from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class SampleRecord:
    sample_id: str

    # design variables
    x_raw: Dict[str, float]
    x_norm: Optional[Dict[str, float]] = None

    # simulation outputs
    y: Optional[Dict[str, float]] = None

    # feasibility and constraints
    is_feasible: Optional[bool] = None
    constraint_satisfaction: Dict[str, bool] = field(default_factory=dict)
    constraint_violation: Dict[str, float] = field(default_factory=dict)

    # boundary semantics
    boundary_distance: Optional[float] = None
    boundary_label: Optional[str] = None   # safe / boundary / infeasible / failed

    # execution status
    simulation_success: Optional[bool] = None
    failure_type: Optional[str] = None
    simulation_time_sec: Optional[float] = None

    # provenance
    source_stage: Optional[str] = None     # initial / active / optimization / hard_case
    seed: Optional[int] = None
    dataset_version: Optional[str] = None
    config_name: Optional[str] = None

    # metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "x_raw": self.x_raw,
            "x_norm": self.x_norm,
            "y": self.y,
            "is_feasible": self.is_feasible,
            "constraint_satisfaction": self.constraint_satisfaction,
            "constraint_violation": self.constraint_violation,
            "boundary_distance": self.boundary_distance,
            "boundary_label": self.boundary_label,
            "simulation_success": self.simulation_success,
            "failure_type": self.failure_type,
            "simulation_time_sec": self.simulation_time_sec,
            "source_stage": self.source_stage,
            "seed": self.seed,
            "dataset_version": self.dataset_version,
            "config_name": self.config_name,
            "created_at": self.created_at,
        }