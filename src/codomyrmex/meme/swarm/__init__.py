"""codomyrmex.meme.swarm — Swarm Intelligence & Collective Behavior."""

from codomyrmex.meme.swarm.consensus import quorum_sensing, reach_consensus
from codomyrmex.meme.swarm.engine import SwarmEngine
from codomyrmex.meme.swarm.flocking import update_flock
from codomyrmex.meme.swarm.models import (
    ConsensusState,
    EmergentPattern,
    FlockingParams,
    SwarmAgent,
    SwarmState,
)

__all__ = [
    "SwarmAgent",
    "SwarmState",
    "FlockingParams",
    "EmergentPattern",
    "ConsensusState",
    "SwarmEngine",
    "update_flock",
    "reach_consensus",
    "quorum_sensing",
]
