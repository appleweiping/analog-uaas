from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import json
from src.simulation.mock_simulator import simulate
from src.data.schema import SampleRecord

INPUT_PATH = Path("data/interim/initial_designs.json")
OUTPUT_PATH = Path("data/processed/dataset_v0.json")


def check_constraints(y: dict):
    sat = {
        "gain_db": y["gain_db"] >= 60.0,
        "gbw_hz": y["gbw_hz"] >= 1.0e6,
        "phase_margin_deg": y["phase_margin_deg"] >= 60.0,
        "power_w": y["power_w"] <= 1.0e-3,
    }
    violation = {
        "gain_db": max(0.0, 60.0 - y["gain_db"]),
        "gbw_hz": max(0.0, 1.0e6 - y["gbw_hz"]),
        "phase_margin_deg": max(0.0, 60.0 - y["phase_margin_deg"]),
        "power_w": max(0.0, y["power_w"] - 1.0e-3),
    }
    feasible = all(sat.values())
    return feasible, sat, violation


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        designs = json.load(f)

    dataset = []
    for item in designs:
        x_raw = item["x_raw"]
        y = simulate(x_raw)
        feasible, sat, violation = check_constraints(y)

        rec = SampleRecord(
            sample_id=item["sample_id"],
            x_raw=x_raw,
            y=y,
            is_feasible=feasible,
            constraint_satisfaction=sat,
            constraint_violation=violation,
            simulation_success=True,
            boundary_label="unknown",
            source_stage="initial",
            dataset_version="v0_initial",
            config_name="exp_main",
        )
        dataset.append(rec.to_dict())

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"Saved dataset to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()