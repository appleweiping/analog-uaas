from __future__ import annotations

import argparse

from src.utils.io import load_yaml, dump_json
from src.circuits.opamp_design_space import TwoStageOpAmpCircuit
from src.circuits.netlist_writer import NetlistWriter
from src.simulation.spectre_runner import SpectreRunner
from src.simulation.result_parser import ResultParser
from src.simulation.failure_checker import FailureChecker


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/circuit/opamp_real.yaml")
    parser.add_argument("--out", type=str, default="data/interim/opamp_real_validation.json")
    args = parser.parse_args()

    config = load_yaml(args.config)
    circuit = TwoStageOpAmpCircuit(config)
    design = circuit.sample_designs(n=1, seed=config["sampling"]["seed"])[0]
    netlist_params = circuit.to_netlist_params(design)

    writer = NetlistWriter(config["paths"]["template_netlist"])
    runner = SpectreRunner(config["simulation"])
    parser_ = ResultParser()
    checker = FailureChecker()

    run_id = "real_validation_000000"
    netlist_path = f'{config["paths"]["generated_netlists_dir"]}/{run_id}.scs'
    run_dir = f'{config["paths"]["raw_results_dir"]}/{run_id}'

    writer.write(netlist_path, netlist_params)
    runner_result = runner.run(
        netlist_path=netlist_path,
        run_dir=run_dir,
        metadata={"run_id": run_id, "seed": config["sampling"]["seed"], "design": design},
    )
    metrics = parser_.parse(runner_result["metrics_path"], runner_result["log_path"])
    failure = checker.check(runner_result, metrics)

    summary = {
        "design": design,
        "netlist_path": netlist_path,
        "run_dir": run_dir,
        "runner_result": runner_result,
        "metrics": metrics,
        "failure": {
            "simulation_failed": failure.simulation_failed,
            "failure_reasons": failure.failure_reasons,
            "metrics_complete": failure.metrics_complete,
        },
    }
    dump_json(summary, args.out)

    print("[validate_real_simulation] finished")
    print(f"[validate_real_simulation] failed={failure.simulation_failed}")
    print(f"[validate_real_simulation] metrics={metrics}")
    print(f"[validate_real_simulation] output={args.out}")


if __name__ == "__main__":
    main()