from __future__ import annotations

import argparse
import statistics
from collections import Counter, defaultdict

from src.utils.io import load_json, dump_json


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    idx = int((len(values) - 1) * q)
    return values[idx]


def summarize_metric(values: list[float]) -> dict:
    if not values:
        return {"count": 0, "mean": None, "p50": None, "p90": None, "min": None, "max": None}
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "p50": quantile(values, 0.50),
        "p90": quantile(values, 0.90),
        "min": min(values),
        "max": max(values),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", type=str, default="data/processed/opamp/opamp_results_flat.json")
    parser.add_argument("--out", type=str, default="data/processed/opamp/opamp_results_summary.json")
    args = parser.parse_args()

    rows = load_json(args.infile)

    total = len(rows)
    failed = [r for r in rows if r.get("simulation_failed", False)]
    success = [r for r in rows if not r.get("simulation_failed", False)]
    feasible = [r for r in success if r.get("is_feasible", False)]
    infeasible = [r for r in success if not r.get("is_feasible", False)]

    failure_reason_counter = Counter()
    violation_counter = Counter()

    metric_values = defaultdict(list)
    design_values = defaultdict(list)

    for r in rows:
        reason = r.get("failure_reasons", "") or r.get("failure_reason", "")
        if reason:
            if isinstance(reason, str):
                for token in reason.split(";"):
                    token = token.strip()
                    if token:
                        failure_reason_counter[token] += 1

        for k, v in r.items():
            if k.startswith("metric__") and v is not None and not r.get("simulation_failed", False):
                try:
                    metric_values[k].append(float(v))
                except Exception:
                    pass
            if k.startswith("design__") and v is not None:
                try:
                    design_values[k].append(float(v))
                except Exception:
                    pass
            if k.startswith("violation__") and v is not None:
                try:
                    if float(v) > 0:
                        violation_counter[k] += 1
                except Exception:
                    pass

    summary = {
        "total_samples": total,
        "failed_samples": len(failed),
        "failed_ratio": len(failed) / total if total else 0.0,
        "successful_samples": len(success),
        "feasible_samples": len(feasible),
        "feasible_ratio_over_total": len(feasible) / total if total else 0.0,
        "feasible_ratio_over_success": len(feasible) / len(success) if success else 0.0,
        "infeasible_samples": len(infeasible),
        "failure_reason_breakdown": dict(failure_reason_counter),
        "violation_breakdown": dict(violation_counter),
        "metrics_summary": {k: summarize_metric(v) for k, v in metric_values.items()},
        "design_summary": {k: summarize_metric(v) for k, v in design_values.items()},
    }

    dump_json(summary, args.out)

    print("=== RESULTS SUMMARY ===")
    print(f"Total: {summary['total_samples']}")
    print(f"Failed: {summary['failed_samples']} ({summary['failed_ratio']:.2%})")
    print(f"Successful: {summary['successful_samples']}")
    print(f"Feasible: {summary['feasible_samples']} ({summary['feasible_ratio_over_total']:.2%} of total)")
    print(f"Infeasible: {summary['infeasible_samples']}")
    print("Failure breakdown:", summary["failure_reason_breakdown"])
    print("Violation breakdown:", summary["violation_breakdown"])
    print(f"Saved summary to {args.out}")


if __name__ == "__main__":
    main()