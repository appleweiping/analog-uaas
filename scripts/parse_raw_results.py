from __future__ import annotations

import argparse
from typing import Dict, Any, List

from src.utils.io import load_json, dump_csv, dump_json


def flatten_record(record: Dict[str, Any]) -> Dict[str, Any]:
    flat: Dict[str, Any] = {
        "run_id": record["run_id"],
        "simulation_failed": record["simulation_failed"],
        "metrics_complete": record["metrics_complete"],
        "is_feasible": record["is_feasible"],
        "runtime_sec": record["runner_result"].get("runtime_sec", None),
        "mode": record["runner_result"].get("mode", ""),
        "failure_reasons": "; ".join(record.get("failure_reasons", [])),
        "netlist_path": record.get("netlist_path", ""),
        "run_dir": record.get("run_dir", ""),
    }

    for k, v in record.get("design", {}).items():
        flat[f"design__{k}"] = v

    for k, v in record.get("metrics", {}).items():
        flat[f"metric__{k}"] = v

    for k, v in record.get("violations", {}).items():
        flat[f"violation__{k}"] = v

    for k, v in record.get("margins", {}).items():
        flat[f"margin__{k}"] = v

    return flat


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", type=str, default="data/interim/opamp_batch_results.json")
    parser.add_argument("--out_csv", type=str, default="data/processed/opamp/opamp_results_flat.csv")
    parser.add_argument("--out_json", type=str, default="data/processed/opamp/opamp_results_flat.json")
    args = parser.parse_args()

    records = load_json(args.infile)
    flat_rows: List[Dict[str, Any]] = [flatten_record(r) for r in records]

    dump_csv(flat_rows, args.out_csv)
    dump_json(flat_rows, args.out_json)

    print(f"[parse_raw_results] exported {len(flat_rows)} rows")
    print(f"[parse_raw_results] csv -> {args.out_csv}")
    print(f"[parse_raw_results] json -> {args.out_json}")


if __name__ == "__main__":
    main()