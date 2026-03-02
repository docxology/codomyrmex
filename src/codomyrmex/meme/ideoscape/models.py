"""Data models for information cartography."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class ProjectionType(str, Enum):
    """Map projection types for abstract spaces."""

    MERCATOR = "mercator"  # Preserves angles
    HYPERBOLIC = "hyperbolic"  # Logic space visualization
    TOROIDAL = "toroidal"  # Wraparound (gaming/sims)
    SPHERICAL = "spherical"  # Global view


@dataclass
class CoordinateSystem:
    """Definition of the mapping space."""
    dimensions: int = 2
    bounds: list[float] = field(default_factory=lambda: [-100.0, 100.0, -100.0, 100.0])
    projection: ProjectionType = ProjectionType.MERCATOR


@dataclass
class MapFeature:
    """A distinct feature on the ideoscape map.

    Attributes:
        name: Feature name (e.g. 'Mount Doge').
        position: Coordinates.
        feature_type: Classification (e.g. 'peak', 'valley', 'cluster').
        magnitude: Size/Importance.
    """
    name: str
    position: np.ndarray = field(default_factory=lambda: np.zeros(2))
    feature_type: str = "point"
    magnitude: float = 1.0
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.position, list):
            self.position = np.array(self.position)


@dataclass
class IdeoscapeLayer:
    """A thematic layer of the map.

    Attributes:
        name: Layer name (e.g. 'Sentiment', 'Keywords').
        data_points: Raw data points.
        opacity: Visual weight.
    """
    name: str
    data_points: list[MapFeature] = field(default_factory=list)
    opacity: float = 1.0


@dataclass
class TerrainMap:
    """The generated terrain of the ideoscape.

    Attributes:
        height_map: 2D array representing 'elevation' (e.g. attention/virality).
        resolution: Grid resolution.
        features: Identified features.
    """
    height_map: np.ndarray = field(default_factory=lambda: np.zeros((100, 100)))
    resolution: int = 100
    features: list[MapFeature] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        if isinstance(self.height_map, list):
            self.height_map = np.array(self.height_map)
