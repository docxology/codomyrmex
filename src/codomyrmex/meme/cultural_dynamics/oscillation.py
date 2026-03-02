"""Oscillation detection and modeling."""

from __future__ import annotations

from codomyrmex.meme.cultural_dynamics.models import CulturalState


def detect_oscillation(states: list[CulturalState], dimension: str) -> bool:
    """Detect if a dimension is oscillating."""
    values = [s.dimensions.get(dimension, 0.0) for s in states]
    if len(values) < 3:
        return False

    # Check for sign changes in derivative
    diffs = [y - x for x, y in zip(values[:-1], values[1:], strict=False)]
    sign_changes = sum(1 for i in range(len(diffs)-1) if diffs[i] * diffs[i+1] < 0)

    return sign_changes > 0


def backlash_model(current_value: float, velocity: float) -> float:
    """Model cultural backlash (rubber-band effect).

    Returns the restoring force.
    """
    k = 0.5  # Spring constant
    damping = 0.1

    force = -k * current_value - damping * velocity
    return force
