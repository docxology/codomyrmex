"""Flocking behavior implementation (Boids algorithm)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from codomyrmex.meme.swarm.models import FlockingParams, SwarmAgent


def update_flock(agents: list[SwarmAgent], params: FlockingParams) -> None:
    """Update agent positions and velocities based on flocking rules.

    Applies Separation, Alignment, and Cohesion (Reynolds).
    Modifies agents in-place using spatial hashing to avoid O(N^2) search.
    """
    n = len(agents)
    if n == 0:
        return

    positions = np.array([a.position for a in agents])
    velocities = np.array([a.velocity for a in agents])

    # ⚡ Bolt: Build spatial hash grid for O(N) neighbor lookups
    # (replaces naive O(N^2) pairwise distance check)
    cell_size = params.perception_radius
    if cell_size <= 0:
        cell_size = 1.0  # Fallback to prevent division by zero

    grid: dict[tuple[int, int, int], list[int]] = {}
    for i, pos in enumerate(positions):
        cx = int(pos[0] // cell_size)
        cy = int(pos[1] // cell_size)
        cz = int(pos[2] // cell_size)
        cell_key = (cx, cy, cz)
        if cell_key not in grid:
            grid[cell_key] = []
        grid[cell_key].append(i)

    # 27 adjacent cell offsets to search for neighbors
    offsets = [
        (dx, dy, dz)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        for dz in (-1, 0, 1)
    ]

    accelerations = np.zeros((n, 3))

    for i, agent in enumerate(agents):
        cx = int(agent.position[0] // cell_size)
        cy = int(agent.position[1] // cell_size)
        cz = int(agent.position[2] // cell_size)

        potential_neighbors = []
        for dx, dy, dz in offsets:
            cell_key = (cx + dx, cy + dy, cz + dz)
            if cell_key in grid:
                potential_neighbors.extend(grid[cell_key])

        if not potential_neighbors:
            continue

        p_idx = np.array(potential_neighbors, dtype=int)
        # Remove self from potential neighbors
        p_idx = p_idx[p_idx != i]
        if len(p_idx) == 0:
            continue

        n_pos = positions[p_idx]
        n_vel = velocities[p_idx]

        # Calculate exact distances for agents in nearby cells
        diffs = agent.position - n_pos
        distances = np.linalg.norm(diffs, axis=1)

        valid = (distances > 0) & (distances < params.perception_radius)
        if not np.any(valid):
            continue

        valid_idx = np.where(valid)[0]
        v_diffs = diffs[valid_idx]
        v_dist = distances[valid_idx]
        v_pos = n_pos[valid_idx]
        v_vel = n_vel[valid_idx]

        # Separation: Steer away from neighbors
        inv_dist = 1.0 / (v_dist + 1e-6)
        sep = np.sum(v_diffs * inv_dist[:, np.newaxis], axis=0) / len(valid_idx)

        # Alignment: steer towards average velocity
        ali = np.mean(v_vel, axis=0)

        # Cohesion: steer towards average position
        coh = np.mean(v_pos, axis=0) - agent.position

        # Apply weights (simplified physics)
        acc = (
            sep * params.separation_weight
            + ali * params.alignment_weight
            + coh * params.cohesion_weight
        )

        # Limit force
        norm_acc = np.linalg.norm(acc)
        if norm_acc > params.max_force:
            acc = (acc / norm_acc) * params.max_force

        accelerations[i] = acc

    # Update velocities
    velocities += accelerations

    # Limit speed
    speeds = np.linalg.norm(velocities, axis=1)
    exceed_speed = speeds > params.max_speed
    velocities[exceed_speed] = (
        velocities[exceed_speed] / speeds[exceed_speed][:, np.newaxis]
    ) * params.max_speed

    # Update positions
    positions += velocities

    # Write back to agent objects
    for i, agent in enumerate(agents):
        agent.velocity = velocities[i]
        agent.position = positions[i]
