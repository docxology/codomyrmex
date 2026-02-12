"""Data models for cultural dynamics."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np


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

    dimensions: Dict[str, float] = field(default_factory=dict)
    momentum: Dict[str, float] = field(default_factory=dict)
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
    states: List[CulturalState] = field(default_factory=list)
    trend_vector: Optional[Dict[str, float]] = None


@dataclass
class PowerMap:
    """Mapping of sociopolitical power dynamics.

    Attributes:
        nodes: Entities with power.
        influence_matrix: Directed influence weights.
        capital_flows: Flow of capital (symbolic/material) between nodes.
    """
    nodes: List[str] = field(default_factory=list)
    # Simplified representation for now
    centrality_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class FrequencyMap:
    """Spectral analysis of cultural oscillations."""
    dimension: str
    dominant_frequency: float
    period: float
    amplitude: float
