"""Flocking behavior implementation (Boids algorithm)."""

from __future__ import annotations

import numpy as np

from codomyrmex.meme.swarm.models import FlockingParams, SwarmAgent


def update_flock(agents: list[SwarmAgent], params: FlockingParams) -> None:
    """Update agent positions and velocities based on flocking rules.

    Applies Separation, Alignment, and Cohesion (Reynolds).
    Modifies agents in-place.
    """
    positions = np.array([a.position for a in agents])
    velocities = np.array([a.velocity for a in agents])

    n = len(agents)
    if n == 0:
        return

    for i, agent in enumerate(agents):
        # Find neighbors within radius
        # (Naive O(N^2) for now - optimize with spatial tree later)
        distances = np.linalg.norm(positions - agent.position, axis=1)
        neighbors = (distances > 0) & (distances < params.perception_radius)

        sep = np.zeros(3)
        ali = np.zeros(3)
        coh = np.zeros(3)

        if np.any(neighbors):
            # Separation: Steer away from neighbors
            diffs = agent.position - positions[neighbors]
            inv_dist = 1.0 / (distances[neighbors][:, np.newaxis] + 1e-6)
            sep = np.sum(diffs * inv_dist, axis=0) / np.sum(neighbors)

            # Alignment: steer towards average velocity
            ali = np.mean(velocities[neighbors], axis=0)

            # Cohesion: steer towards average position
            coh = np.mean(positions[neighbors], axis=0) - agent.position

        # Normalize and weigh
        def steer(vec, target):
            """steer ."""
            # Helper to implement "steer towards" logic not fully expanded
            # for brevity in this snippet, using raw forces directly:
            return vec

        # Apply weights (simplified physics)
        acceleration = (
            sep * params.separation_weight +
            ali * params.alignment_weight +
            coh * params.cohesion_weight
        )

        # Limit force
        norm_acc = np.linalg.norm(acceleration)
        if norm_acc > params.max_force:
            acceleration = (acceleration / norm_acc) * params.max_force

        # Update
        agent.velocity += acceleration

        # Limit speed
        speed = np.linalg.norm(agent.velocity)
        if speed > params.max_speed:
            agent.velocity = (agent.velocity / speed) * params.max_speed

        agent.position += agent.velocity
