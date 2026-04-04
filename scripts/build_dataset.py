from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from src.circuits.constraints import evaluate_specs
from src.data.boundary_tagging import BoundaryTagger
from src.data.dataset import AnalogDataset
from src.data.normalization import StandardNormalizer
from src.data.schema import SampleRecord
from src.data.split import DatasetSplitter, SplitConfig
from src.utils.io import dump_json, load_json, load_yaml


def infer_failure_type(failure_reasons: List[str]) -> str | None:
    if not failure_reasons:
        return None
    if any("simulation_error" in item for item in failure_reasons):
        return "simulation_error"
    if any("metrics_missing" in item for item in failure_reasons):
        return "metrics_missing"
    if any("metrics_file_missing" in item for item in failure_reasons):
        return "metrics_file_missing"
    return failure_reasons[0]


def build_records(
    batch_results: List[Dict[str, Any]],
    config: Dict[str, Any],
    dataset_version: str,
    source_stage: str,
    boundary_epsilon: float,
) -> List[SampleRecord]:
    constraints_cfg = config["constraints"]
    environment_cfg = config.get("environment", {})
    boundary_tagger = BoundaryTagger(boundary_epsilon=boundary_epsilon)
    records: List[SampleRecord] = []

    for item in batch_results:
        run_id = item["run_id"]
        design = {str(k): float(v) for k, v in item.get("design", {}).items()}
        metrics = {str(k): float(v) for k, v in item.get("metrics", {}).items()}
        failure_reasons = list(item.get("failure_reasons", []))
        simulation_failed = bool(item.get("simulation_failed", False))

        if simulation_failed:
            tag_result = boundary_tagger.tag(
                margins={"failed_margin": -1.0},
                simulation_failed=True,
                failure_reasons=failure_reasons,
            )
            spec_result = None
        else:
            spec_result = evaluate_specs(metrics, constraints_cfg)
            tag_result = boundary_tagger.tag(
                margins=spec_result.margins,
                simulation_failed=False,
                failure_reasons=failure_reasons,
            )

        record = SampleRecord(
            sample_id=run_id,
            run_id=run_id,
            x_raw=design,
            environment=environment_cfg,
            y=metrics,
            is_feasible=(False if spec_result is None else spec_result.is_feasible),
            overall_spec_satisfied=(False if spec_result is None else spec_result.is_feasible),
            constraint_satisfaction=tag_result.constraint_satisfaction,
            constraint_violation=(
                {} if spec_result is None else dict(spec_result.violations)
            ),
            constraint_margin=(
                {} if spec_result is None else dict(spec_result.margins)
            ),
            nearest_constraint=tag_result.nearest_constraint,
            boundary_distance=tag_result.boundary_distance,
            boundary_label=tag_result.label,
            simulation_success=not simulation_failed,
            simulation_failed=simulation_failed,
            failure_type=infer_failure_type(failure_reasons),
            failure_reasons=failure_reasons,
            metrics_complete=bool(item.get("metrics_complete", not simulation_failed)),
            simulation_time_sec=item.get("runner_result", {}).get("runtime_sec"),
            source_stage=source_stage,
            seed=item.get("runner_result", {}).get("metadata", {}).get("seed", item.get("seed")),
            dataset_version=dataset_version,
            config_name=config.get("name", "unknown_circuit"),
            tags={
                "mode": item.get("runner_result", {}).get("mode", "unknown"),
                "netlist_path": item.get("netlist_path"),
                "run_dir": item.get("run_dir"),
            },
        )
        records.append(record)

    # fit normalization using only successful samples
    success_records = [r for r in records if not r.simulation_failed]
    if success_records:
        x_norm = StandardNormalizer().fit([r.x_raw for r in success_records])
        y_norm = StandardNormalizer().fit([r.y for r in success_records])
        for record in records:
            if not record.simulation_failed:
                record.x_norm = x_norm.transform_row(record.x_raw)
                record.y_norm = y_norm.transform_row(record.y)

    return records


def attach_splits(records: List[SampleRecord], seed: int) -> Dict[str, List[int]]:
    splitter = DatasetSplitter(SplitConfig(seed=seed))
    split_indices = splitter.split_indices(len(records))
    for idx in split_indices.train:
        records[idx].split = "train"
    for idx in split_indices.val:
        records[idx].split = "val"
    for idx in split_indices.test:
        records[idx].split = "test"
    return split_indices.to_dict()


def build_summary(dataset: AnalogDataset, split_indices: Dict[str, List[int]]) -> Dict[str, Any]:
    summary = dataset.summary()
    summary["splits"] = {key: len(value) for key, value in split_indices.items()}
    summary["avg_runtime_sec"] = (
        sum(r.simulation_time_sec or 0.0 for r in dataset.records) / max(len(dataset.records), 1)
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/circuit/opamp.yaml")
    parser.add_argument("--infile", type=str, default="data/interim/opamp_batch_results.json")
    parser.add_argument("--out", type=str, default="data/processed/opamp/dataset_v1.json")
    parser.add_argument("--summary_out", type=str, default="data/processed/opamp/dataset_v1_summary.json")
    parser.add_argument("--dataset_version", type=str, default="v1_stage3")
    parser.add_argument("--source_stage", type=str, default="initial")
    parser.add_argument("--split_seed", type=int, default=42)
    parser.add_argument("--boundary_epsilon", type=float, default=0.10)
    args = parser.parse_args()

    config = load_yaml(args.config)
    batch_results = load_json(args.infile)

    records = build_records(
        batch_results=batch_results,
        config=config,
        dataset_version=args.dataset_version,
        source_stage=args.source_stage,
        boundary_epsilon=args.boundary_epsilon,
    )
    split_indices = attach_splits(records, seed=args.split_seed)
    dataset = AnalogDataset(records)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    dataset.to_json(args.out)
    dump_json(build_summary(dataset, split_indices), args.summary_out)

    print(f"[build_dataset] total={len(dataset)}")
    print(f"[build_dataset] out={args.out}")
    print(f"[build_dataset] summary={args.summary_out}")


if __name__ == "__main__":
    main()