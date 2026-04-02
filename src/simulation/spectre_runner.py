from __future__ import annotations

import json
import math
import random
import shlex
import subprocess
import time
from pathlib import Path
from typing import Dict, Any

from src.simulation.simulator_interface import SimulatorInterface


class SpectreRunner(SimulatorInterface):
    def __init__(self, sim_cfg: Dict[str, Any]) -> None:
        self.sim_cfg = sim_cfg
        self.use_mock = bool(sim_cfg.get("use_mock", False))
        self.spectre_binary = sim_cfg.get("spectre_binary", "spectre")
        self.timeout_sec = int(sim_cfg.get("timeout_sec", 120))
        self.log_filename = sim_cfg.get("log_filename", "spectre.out")
        self.stderr_filename = sim_cfg.get("stderr_filename", "spectre.err")
        self.metrics_filename = sim_cfg.get("metrics_filename", "metrics.txt")
        self.extract_metrics_cmd = sim_cfg.get("extract_metrics_cmd", "").strip()

    def _write_mock_metrics(
        self,
        metrics_path: Path,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        metadata = metadata or {}
        design = metadata.get("design", {})
        seed = int(metadata.get("seed", 0))
        run_id = str(metadata.get("run_id", "0"))

        local_seed = seed + sum(ord(ch) for ch in run_id)
        rng = random.Random(local_seed)

        w_in = float(design.get("w_in", 10e-6))
        l_in = float(design.get("l_in", 0.5e-6))
        w_stage2 = float(design.get("w_stage2", 20e-6))
        c_comp = float(design.get("c_comp", 1e-12))
        i_bias = float(design.get("i_bias", 50e-6))
        w_load = float(design.get("w_load", 10e-6))

        # 下面这个 mock 模型不追求物理精确，只追求“有合理趋势、能制造可行/不可行/失败样本”
        gain_db = (
            45
            + 8.0 * math.log10(max(w_in / l_in, 1.0))
            + 4.0 * math.log10(max(w_load / l_in, 1.0))
            + rng.gauss(0, 1.5)
        )

        gbw_hz = (
            3e6
            * max(i_bias / max(c_comp, 1e-15), 1.0)
            * 1e-6
            * max(w_stage2 / max(w_in, 1e-15), 0.2)
            * math.exp(rng.gauss(0, 0.08))
        )

        pm_deg = (
            80
            - 15.0 * math.log10(max(w_stage2 / max(w_in, 1e-15), 0.1))
            + 10.0 * math.log10(max(c_comp / 1e-12, 0.1))
            + rng.gauss(0, 2.0)
        )

        power_w = 1.8 * i_bias * (1.0 + 0.2 * (w_stage2 / max(w_in, 1e-15))) + abs(rng.gauss(0, 2e-5))

        # 故意构造一部分“数值仿真失败”，后面用于 failure_checker 测试
        unstable_score = (w_stage2 / max(w_in, 1e-15)) / max(c_comp / 1e-12, 0.05)
        fail_prob = 0.02
        if unstable_score > 12:
            fail_prob = 0.25
        elif unstable_score > 8:
            fail_prob = 0.10

        if rng.random() < fail_prob:
            metrics_path.write_text("simulation_failed=1\n", encoding="utf-8")
            return

        text = (
            f"gain_db={gain_db:.6f}\n"
            f"gbw_hz={gbw_hz:.6f}\n"
            f"pm_deg={pm_deg:.6f}\n"
            f"power_w={power_w:.9f}\n"
        )
        metrics_path.write_text(text, encoding="utf-8")

    def _run_mock(
        self,
        netlist_path: Path,
        run_dir: Path,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        start = time.time()
        log_path = run_dir / self.log_filename
        stderr_path = run_dir / self.stderr_filename
        metrics_path = run_dir / self.metrics_filename

        log_path.write_text("MOCK spectre run successful.\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        self._write_mock_metrics(metrics_path, metadata=metadata)

        runtime = time.time() - start
        return {
            "success": True,
            "return_code": 0,
            "runtime_sec": runtime,
            "run_dir": str(run_dir),
            "log_path": str(log_path),
            "stderr_path": str(stderr_path),
            "metrics_path": str(metrics_path),
            "error_message": "",
            "mode": "mock",
        }

    def _run_real(
        self,
        netlist_path: Path,
        run_dir: Path,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        start = time.time()

        log_path = run_dir / self.log_filename
        stderr_path = run_dir / self.stderr_filename
        metrics_path = run_dir / self.metrics_filename

        cmd = [
            self.spectre_binary,
            str(netlist_path),
            "+log",
            str(log_path),
        ]

        with stderr_path.open("w", encoding="utf-8") as ferr:
            proc = subprocess.run(
                cmd,
                cwd=run_dir,
                stdout=subprocess.DEVNULL,
                stderr=ferr,
                timeout=self.timeout_sec,
                check=False,
            )

        if proc.returncode == 0 and self.extract_metrics_cmd:
            fmt_cmd = self.extract_metrics_cmd.format(
                run_dir=str(run_dir),
                netlist_path=str(netlist_path),
            )
            subprocess.run(
                shlex.split(fmt_cmd),
                cwd=run_dir,
                timeout=self.timeout_sec,
                check=False,
            )

        runtime = time.time() - start
        return {
            "success": proc.returncode == 0,
            "return_code": proc.returncode,
            "runtime_sec": runtime,
            "run_dir": str(run_dir),
            "log_path": str(log_path),
            "stderr_path": str(stderr_path),
            "metrics_path": str(metrics_path),
            "error_message": "" if proc.returncode == 0 else f"spectre failed with code {proc.returncode}",
            "mode": "real",
        }

    def run(
        self,
        netlist_path: str | Path,
        run_dir: str | Path,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        netlist_path = Path(netlist_path)
        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)

        if self.use_mock:
            result = self._run_mock(netlist_path, run_dir, metadata)
        else:
            result = self._run_real(netlist_path, run_dir, metadata)

        meta_path = run_dir / "runner_meta.json"
        meta_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return result