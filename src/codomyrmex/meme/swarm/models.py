"""Data models for swarm intelligence."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

import numpy as np


@dataclass
class SwarmAgent:
    """A single agent within a swarm.

    Attributes:
        id: Unique identifier.
        position: 3D coordinates [x, y, z].
        velocity: 3D velocity vector [vx, vy, vz].
        state: Internal state (e.g. 'foraging', 'defending').
        integrity: Health/status (0-1).
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    state: str = "idle"
    integrity: float = 1.0

    def __post_init__(self):
        # Ensure numpy arrays are correct shape/type if passed as lists (common in JSON)
        if isinstance(self.position, list):
            self.position = np.array(self.position, dtype=float)
        if isinstance(self.velocity, list):
            self.velocity = np.array(self.velocity, dtype=float)


@dataclass
class FlockingParams:
    """Parameters controlling flocking behavior (Reynolds)."""
    separation_weight: float = 1.5
    alignment_weight: float = 1.0
    cohesion_weight: float = 1.0
    max_speed: float = 5.0
    max_force: float = 0.1
    perception_radius: float = 10.0


@dataclass
class SwarmState:
    """Snapshot of the entire swarm."""
    agents: list[SwarmAgent] = field(default_factory=list)
    centroid: np.ndarray = field(default_factory=lambda: np.zeros(3))
    avg_velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    coherence: float = 0.0  # Measure of order (0-1)
    timestamp: float = field(default_factory=time.time)


@dataclass
class EmergentPattern:
    """A detected pattern emerging from collective behavior.

    Attributes:
        pattern_type: Type of pattern (e.g. 'vortex', 'line', 'cluster').
        strength: Confidence/Strength of pattern (0-1).
        duration: How long it has persisted.
    """
    pattern_type: str
    strength: float = 0.0
    duration: float = 0.0
    involved_agents: list[str] = field(default_factory=list)


@dataclass
class ConsensusState:
    """State of a consensus process.

    Attributes:
        proposal_id: ID of the proposal.
        round: Current voting round.
        agreed_ratio: Percentage of agents in agreement.
        status: 'pending', 'reached', 'failed'.
    """
    proposal_id: str
    round: int = 0
    agreed_ratio: float = 0.0
    status: str = "pending"
