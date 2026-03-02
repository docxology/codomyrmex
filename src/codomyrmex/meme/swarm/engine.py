"""SwarmEngine — high-level orchestrator for swarm systems."""

from __future__ import annotations

from codomyrmex.meme.swarm.flocking import update_flock
from codomyrmex.meme.swarm.models import FlockingParams, SwarmAgent, SwarmState


class SwarmEngine:
    """Engine for simulating and controlling agent swarms."""

    def __init__(self, num_agents: int = 50):
        """Initialize this instance."""
        self.agents = [SwarmAgent() for _ in range(num_agents)]
        self.params = FlockingParams()

    def step(self) -> SwarmState:
        """Advance simulation by one step."""
        update_flock(self.agents, self.params)

        # Compute state metrics
        import numpy as np
        positions = np.array([a.position for a in self.agents])
        velocities = np.array([a.velocity for a in self.agents])

        centroid = np.mean(positions, axis=0)
        avg_vel = np.mean(velocities, axis=0)

        # Coherence: alignment consistency
        speeds = np.linalg.norm(velocities, axis=1)
        # Avoid div by zero
        norm_vels = velocities / (speeds[:, np.newaxis] + 1e-6)
        # Length of mean normalized velocity vector
        coherence = float(np.linalg.norm(np.mean(norm_vels, axis=0)))

        return SwarmState(
            agents=self.agents,
            centroid=centroid,
            avg_velocity=avg_vel,
            coherence=coherence
        )
