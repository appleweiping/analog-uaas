from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any


class SimulatorInterface(ABC):
    @abstractmethod
    def run(
        self,
        netlist_path: str | Path,
        run_dir: str | Path,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Execute one simulation job.

        Returns a dict with at least:
        {
            "success": bool,
            "return_code": int,
            "runtime_sec": float,
            "run_dir": str,
            "log_path": str,
            "stderr_path": str,
            "metrics_path": str,
            "error_message": str,
        }
        """
        raise NotImplementedError