"""Benchmark comparison utilities.

Provides helpers for comparing benchmark results across runs,
generating delta tables, and computing statistical significance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class BenchmarkDelta:
    """Delta between two benchmark values.

    Attributes:
        name: Benchmark identifier.
        before: Previous value.
        after: Current value.
        absolute_delta: after - before.
        relative_delta: Percentage change.
        improved: Whether the change is an improvement.
    """

    name: str
    before: float
    after: float
    absolute_delta: float
    relative_delta: float
    improved: bool


def compute_delta(
    name: str,
    before: float,
    after: float,
    higher_is_better: bool = False,
) -> BenchmarkDelta:
    """Compute the delta between two benchmark measurements.

    Args:
        name: Benchmark identifier.
        before: Previous value.
        after: New value.
        higher_is_better: If True, increase = improvement.

    Returns:
        BenchmarkDelta with computed fields.
    """
    absolute = after - before
    relative = (absolute / before * 100) if before != 0 else 0.0

    if higher_is_better:
        improved = after > before
    else:
        improved = after < before

    return BenchmarkDelta(
        name=name,
        before=before,
        after=after,
        absolute_delta=absolute,
        relative_delta=relative,
        improved=improved,
    )


def mean(values: list[float]) -> float:
    """Compute arithmetic mean of a list of values."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def stddev(values: list[float]) -> float:
    """Compute sample standard deviation."""
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def coefficient_of_variation(values: list[float]) -> float:
    """Compute coefficient of variation (CV) as a percentage.

    CV = (stddev / mean) * 100. Returns 0.0 if mean is zero.
    """
    m = mean(values)
    if m == 0:
        return 0.0
    return (stddev(values) / abs(m)) * 100
