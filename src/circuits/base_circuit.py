from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseCircuit(ABC):
    """Abstract circuit design space interface."""

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        self.name = name
        self.config = config

    @abstractmethod
    def sample_design(self, rng) -> Dict[str, float]:
        """Sample one valid design point."""
        raise NotImplementedError

    @abstractmethod
    def sample_designs(self, n: int, seed: int | None = None) -> List[Dict[str, float]]:
        """Sample multiple valid design points."""
        raise NotImplementedError

    @abstractmethod
    def validate_design(self, design: Dict[str, float]) -> tuple[bool, List[str]]:
        """Check design-space validity before simulation."""
        raise NotImplementedError

    @abstractmethod
    def to_netlist_params(self, design: Dict[str, float]) -> Dict[str, Any]:
        """Convert design vector into netlist parameter mapping."""
        raise NotImplementedError