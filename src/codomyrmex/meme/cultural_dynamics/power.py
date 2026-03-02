"""Power dynamics mapping."""

from __future__ import annotations

from codomyrmex.meme.cultural_dynamics.models import PowerMap


def map_power_dynamics(entities: list[str], flows: list[tuple[str, str, float]]) -> PowerMap:
    """Map power based on capital flows.

    Args:
        entities: List of entity IDs.
        flows: List of (source, target, amount) tuples.
    """
    scores = dict.fromkeys(entities, 0.0)

    # Simple net flow calculation
    for src, dst, amount in flows:
        if src in scores:
            scores[src] -= amount * 0.5  # Spending
        if dst in scores:
            scores[dst] += amount      # Accumulating

    # Normalize
    max_score = max(scores.values()) if scores else 1.0
    if max_score == 0:
        max_score = 1.0

    normalized = {k: v / max_score for k, v in scores.items()}

    return PowerMap(nodes=entities, centrality_scores=normalized)
