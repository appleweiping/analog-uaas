from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Any, List

from src.utils.io import load_yaml, dump_json
from src.circuits.opamp_design_space import TwoStageOpAmpCircuit


def build_samples(config: Dict[str, Any], n: int, seed: int) -> List[Dict[str, Any]]:
    circuit = TwoStageOpAmpCircuit(config)
    designs = circuit.sample_designs(n=n, seed=seed)

    samples = []
    for idx, design in enumerate(designs):
        run_id = f"run_{idx:06d}"
        samples.append(
            {
                "run_id": run_id,
                "seed": seed,
                "design": design,
                "netlist_params": circuit.to_netlist_params(design),
            }
        )
    return samples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/circuit/opamp.yaml")
    parser.add_argument("--n", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--out", type=str, default="data/interim/opamp_initial_samples.json")
    args = parser.parse_args()

    config = load_yaml(args.config)
    sampling_cfg = config.get("sampling", {})
    n = args.n if args.n is not None else int(sampling_cfg.get("n_initial", 64))
    seed = args.seed if args.seed is not None else int(sampling_cfg.get("seed", 42))

    samples = build_samples(config=config, n=n, seed=seed)
    dump_json(samples, args.out)

    print(f"[generate_initial_designs] saved {len(samples)} samples to {args.out}")


if __name__ == "__main__":
    main()