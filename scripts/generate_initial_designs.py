import json
import os
import uuid
from pathlib import Path

OUTPUT_PATH = Path("data/interim/initial_designs.json")


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    designs = []
    for _ in range(10):
        designs.append(
            {
                "sample_id": str(uuid.uuid4()),
                "x_raw": {
                    "W_in": 5e-6,
                    "L_in": 0.18e-6,
                    "W_load": 8e-6,
                    "L_load": 0.18e-6,
                    "W_stage2": 20e-6,
                    "L_stage2": 0.18e-6,
                    "I_bias": 10e-6,
                    "Cc": 1e-12,
                }
            }
        )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(designs, f, indent=2)

    print(f"Saved initial designs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()