"""Stigmergy value objects — environmental traces (quantitative markers)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceMarker:
    """A single stigmergic trace: strength decays over time unless reinforced."""

    key: str
    strength: float
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StigmergyConfig:
    """Rates and bounds for trace deposition, reinforcement, and evaporation."""

    evaporation_per_tick: float = 0.1
    reinforce_on_read_delta: float = 0.15
    min_strength: float = 0.0
    max_strength: float = 10.0

    def __post_init__(self) -> None:
        if self.evaporation_per_tick < 0:
            raise ValueError("evaporation_per_tick must be non-negative")
        if self.reinforce_on_read_delta < 0:
            raise ValueError("reinforce_on_read_delta must be non-negative")
        if self.min_strength > self.max_strength:
            raise ValueError("min_strength must not exceed max_strength")
