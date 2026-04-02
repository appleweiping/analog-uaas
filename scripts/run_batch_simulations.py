from __future__ import annotations

import argparse
from pathlib import Path

from src.utils.io import load_yaml, load_json, dump_json
from src.circuits.netlist_writer import NetlistWriter
from src.simulation.spectre_runner import SpectreRunner
from src.simulation.result_parser import ResultParser
from src.simulation.failure_checker import FailureChecker
from src.simulation.job_manager import JobManager


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/circuit/opamp.yaml")
    parser.add_argument("--samples", type=str, default="data/interim/opamp_initial_samples.json")
    parser.add_argument("--out", type=str, default="data/interim/opamp_batch_results.json")
    args = parser.parse_args()

    config = load_yaml(args.config)
    samples = load_json(args.samples)

    template_path = config["paths"]["template_netlist"]
    netlist_writer = NetlistWriter(template_path=template_path)
    runner = SpectreRunner(config["simulation"])
    result_parser = ResultParser()
    failure_checker = FailureChecker()

    manager = JobManager(
        netlist_writer=netlist_writer,
        runner=runner,
        parser=result_parser,
        failure_checker=failure_checker,
        config=config,
    )

    max_workers = int(config["simulation"].get("max_workers", 4))
    results = manager.run_batch(samples=samples, max_workers=max_workers)
    dump_json(results, args.out)

    n_total = len(results)
    n_failed = sum(1 for x in results if x["simulation_failed"])
    n_feasible = sum(1 for x in results if (not x["simulation_failed"]) and x["is_feasible"])

    print(f"[run_batch_simulations] total={n_total}, failed={n_failed}, feasible={n_feasible}")
    print(f"[run_batch_simulations] saved to {args.out}")


if __name__ == "__main__":
    main()