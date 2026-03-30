from pathlib import Path
import sys
import json

# === fix import path ===
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

DATA_PATH = PROJECT_ROOT / "data/processed/dataset_v0.json"


def main():
    if not DATA_PATH.exists():
        print(f"[ERROR] Dataset not found: {DATA_PATH}")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Total samples: {len(data)}")

    if len(data) == 0:
        print("[ERROR] Dataset is empty")
        return

    # === feasibility ===
    feasible_count = sum(d["is_feasible"] for d in data)
    print(f"Feasible ratio: {feasible_count / len(data):.3f}")

    # === simulation failure ===
    failures = [d for d in data if not d["simulation_success"]]
    print(f"Simulation failures: {len(failures)}")

    # === missing values check ===
    missing_y = [i for i, d in enumerate(data) if d["y"] is None]
    if missing_y:
        print(f"[WARNING] Missing y at indices: {missing_y[:5]}")
    else:
        print("All samples have valid y")

    # === constraint logic sanity ===
    wrong_logic = []
    for i, d in enumerate(data):
        y = d["y"]
        if y is None:
            continue

        feasible = d["is_feasible"]

        cond = (
            y["gain_db"] >= 60.0
            and y["gbw_hz"] >= 1e6
            and y["phase_margin_deg"] >= 60.0
            and y["power_w"] <= 1e-3
        )

        if feasible != cond:
            wrong_logic.append(i)

    if wrong_logic:
        print(f"[WARNING] Constraint mismatch at indices: {wrong_logic[:5]}")
    else:
        print("Constraint logic check passed")

    print("✅ Sanity check finished.")


if __name__ == "__main__":
    main()