from __future__ import annotations

from pathlib import Path
from typing import Dict, Any


class NetlistWriter:
    def __init__(self, template_path: str | Path) -> None:
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"template netlist not found: {self.template_path}")
        self.template_text = self.template_path.read_text(encoding="utf-8")

    def render(self, netlist_params: Dict[str, Any]) -> str:
        try:
            return self.template_text.format(**netlist_params)
        except KeyError as exc:
            raise KeyError(f"missing template key for netlist rendering: {exc}") from exc

    def write(self, output_path: str | Path, netlist_params: Dict[str, Any]) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.render(netlist_params)
        output_path.write_text(content, encoding="utf-8")
        return output_path