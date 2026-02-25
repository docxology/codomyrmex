"""Data models for cultural dynamics."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class CulturalState:
    """A snapshot of cultural state along key dimensions.

    Attributes:
        dimensions: Map of dimension names to values (-1 to 1).
            e.g. {'liberty_authority': 0.5, 'tradition_innovation': -0.2}
        momentum: Velocity of change in each dimension.
        energy: Total 'energy' (intensity of discourse).
        timestamp: Time of snapshot.
    """

    dimensions: dict[str, float] = field(default_factory=dict)
    momentum: dict[str, float] = field(default_factory=dict)
    energy: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class Signal:
    """A discrete cultural signal event."""
    source: str
    content: str
    strength: float
    valence: float  # -1 to 1
    dimension: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class Trajectory:
    """A temporal sequence of cultural states."""
    states: list[CulturalState] = field(default_factory=list)
    trend_vector: dict[str, float] | None = None


@dataclass
class PowerMap:
    """Mapping of sociopolitical power dynamics.

    Attributes:
        nodes: Entities with power.
        influence_matrix: Directed influence weights.
        capital_flows: Flow of capital (symbolic/material) between nodes.
    """
    nodes: list[str] = field(default_factory=list)
    # Simplified representation for now
    centrality_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class FrequencyMap:
    """Spectral analysis of cultural oscillations."""
    dimension: str
    dominant_frequency: float
    period: float
    amplitude: float
