from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List

from src.circuits.netlist_writer import NetlistWriter
from src.simulation.result_parser import ResultParser
from src.simulation.failure_checker import FailureChecker
from src.circuits.constraints import evaluate_specs


class JobManager:
    def __init__(
        self,
        netlist_writer: NetlistWriter,
        runner,
        parser: ResultParser,
        failure_checker: FailureChecker,
        config: Dict[str, Any],
    ) -> None:
        self.netlist_writer = netlist_writer
        self.runner = runner
        self.parser = parser
        self.failure_checker = failure_checker
        self.config = config

    def _run_one(
        self,
        sample: Dict[str, Any],
    ) -> Dict[str, Any]:
        paths_cfg = self.config["paths"]
        sim_cfg = self.config["simulation"]
        constraints_cfg = self.config["constraints"]

        run_id = sample["run_id"]
        run_dir = Path(paths_cfg["raw_results_dir"]) / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        netlist_path = Path(paths_cfg["generated_netlists_dir"]) / f"{run_id}.scs"
        self.netlist_writer.write(netlist_path, sample["netlist_params"])

        runner_result = self.runner.run(
            netlist_path=netlist_path,
            run_dir=run_dir,
            metadata={
                "run_id": run_id,
                "seed": sample.get("seed", 0),
                "design": sample["design"],
            },
        )

        metrics = self.parser.parse(
            metrics_path=runner_result["metrics_path"],
            log_path=runner_result["log_path"],
        )

        failure_result = self.failure_checker.check(runner_result, metrics)

        record: Dict[str, Any] = {
            "run_id": run_id,
            "design": sample["design"],
            "netlist_path": str(netlist_path),
            "run_dir": str(run_dir),
            "runner_result": runner_result,
            "metrics": metrics,
            "simulation_failed": failure_result.simulation_failed,
            "failure_reasons": failure_result.failure_reasons,
            "metrics_complete": failure_result.metrics_complete,
        }

        if not failure_result.simulation_failed:
            spec_result = evaluate_specs(metrics, constraints_cfg)
            record["is_feasible"] = spec_result.is_feasible
            record["violations"] = spec_result.violations
            record["margins"] = spec_result.margins
        else:
            record["is_feasible"] = False
            record["violations"] = {}
            record["margins"] = {}

        (run_dir / "record.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return record

    def run_batch(
        self,
        samples: List[Dict[str, Any]],
        max_workers: int,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._run_one, sample) for sample in samples]
            for fut in as_completed(futures):
                results.append(fut.result())
        results.sort(key=lambda x: x["run_id"])
        return results