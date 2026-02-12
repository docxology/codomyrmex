"""Consensus algorithms for distributed swarm agents."""

from __future__ import annotations

from typing import List, Optional
from codomyrmex.meme.swarm.models import SwarmAgent


def reach_consensus(agents: List[SwarmAgent], proposal: str, threshold: float = 0.6) -> bool:
    """Simple majority/threshold consensus check.
    
    Agents are assumed to vote based on internal state (placeholder logic).
    """
    # Placeholder: agents in 'positive' state vote yes
    votes = sum(1 for a in agents if a.state == "positive")
    ratio = votes / len(agents) if agents else 0.0
    return ratio >= threshold


def quorum_sensing(agents: List[SwarmAgent], radius: float) -> float:
    """Calculate local density as a signal for quorum sensing.
    
    Returns average local density (neighbors per unit area/vol).
    """
    total_neighbors = 0
    import numpy as np
    
    positions = np.array([a.position for a in agents])
    
    for i in range(len(agents)):
        dists = np.linalg.norm(positions - positions[i], axis=1)
        count = np.sum(dists < radius) - 1 # Exclude self
        total_neighbors += count
        
    return total_neighbors / len(agents) if agents else 0.0
