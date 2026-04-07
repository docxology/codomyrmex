"""Map trace strength into discrete importance boosts for consolidation."""

from __future__ import annotations


def boost_importance_value(current: int, trace_strength: float) -> int:
    """Raise a 1–4 importance integer using normalized trace strength.

    ``trace_strength`` is a non-negative scalar from a stigmergic ledger; the
    caller may pre-normalize. Thresholds implement a simple quantitative
    stigmergy step: stronger trails bias retention upward.

    Args:
        current: Existing importance ``.value`` (1–4).
        trace_strength: Non-negative trace strength.

    Returns:
        Clamped importance value in ``[1, 4]``.
    """
    if trace_strength <= 0.0:
        return max(1, min(4, current))
    # Treat strength as unbounded positive; use log-like steps
    if trace_strength < 0.5:
        bumped = current
    elif trace_strength < 2.0:
        bumped = current + 1
    else:
        bumped = current + 2
    return max(1, min(4, bumped))


def importance_boost_from_trace(trace_strength: float, *, max_bonus_steps: int = 2) -> int:
    """Return how many integer steps to add to importance (0 … max_bonus_steps)."""
    if trace_strength <= 0.0:
        return 0
    if trace_strength < 0.5:
        return 0
    if trace_strength < 2.0:
        return min(1, max_bonus_steps)
    return min(2, max_bonus_steps)
