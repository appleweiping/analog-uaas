from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Optional


class ResultCache:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _stable_key(payload: Any) -> str:
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def key_for_design(self, design: dict, environment: Optional[dict] = None) -> str:
        return self._stable_key({"design": design, "environment": environment or {}})

    def path_for_key(self, key: str) -> Path:
        prefix = key[:2]
        directory = self.root / prefix
        directory.mkdir(parents=True, exist_ok=True)
        return directory / f"{key}.json"

    def exists(self, key: str) -> bool:
        return self.path_for_key(key).exists()

    def load(self, key: str) -> Optional[Any]:
        path = self.path_for_key(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def save(self, key: str, payload: Any) -> Path:
        path = self.path_for_key(key)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def get_or_none(self, design: dict, environment: Optional[dict] = None) -> Optional[Any]:
        key = self.key_for_design(design=design, environment=environment)
        return self.load(key)