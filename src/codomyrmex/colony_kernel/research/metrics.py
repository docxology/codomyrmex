"""Dependency-light metrics for offline research runs."""

from __future__ import annotations

import math
import random
from collections.abc import Sequence


def _labels(values: Sequence[bool | int | float]) -> list[float]:
    return [1.0 if bool(value) else 0.0 for value in values]


def _validate_probabilities(probabilities: Sequence[float]) -> None:
    if any(not 0.0 <= probability <= 1.0 for probability in probabilities):
        raise ValueError("probabilities must be in [0, 1]")


def log_loss(labels: Sequence[bool | int], probabilities: Sequence[float]) -> float:
    if len(labels) != len(probabilities) or not labels:
        raise ValueError("labels and probabilities must be non-empty and equal length")
    _validate_probabilities(probabilities)
    total = 0.0
    for label, probability in zip(_labels(labels), probabilities, strict=True):
        p = min(1.0 - 1e-12, max(1e-12, probability))
        total += -(label * math.log(p) + (1.0 - label) * math.log(1.0 - p))
    return total / len(labels)


def brier_score(labels: Sequence[bool | int], probabilities: Sequence[float]) -> float:
    if len(labels) != len(probabilities) or not labels:
        raise ValueError("labels and probabilities must be non-empty and equal length")
    _validate_probabilities(probabilities)
    return sum(
        (float(bool(label)) - probability) ** 2
        for label, probability in zip(labels, probabilities, strict=True)
    ) / len(labels)


def confidence_interval(
    values: Sequence[float], confidence: float = 0.95
) -> tuple[float, float]:
    if not values or not 0.0 < confidence < 1.0:
        raise ValueError("values must be non-empty and confidence must be in (0, 1)")
    ordered = sorted(values)
    alpha = (1.0 - confidence) / 2.0
    low = ordered[max(0, min(len(ordered) - 1, int(alpha * len(ordered))))]
    high = ordered[max(0, min(len(ordered) - 1, int((1.0 - alpha) * len(ordered)) - 1))]
    return low, high


def expected_calibration_error(
    labels: Sequence[bool | int], probabilities: Sequence[float], bins: int = 10
) -> float:
    """Return the weighted absolute calibration gap across occupied bins."""
    rows = reliability_bins(labels, probabilities, bins=bins)
    total = len(labels)
    return sum(
        int(row["count"])
        / total
        * abs(float(row["mean_confidence"]) - float(row["empirical_frequency"]))
        for row in rows
    )


def paired_bootstrap_delta(
    baseline: Sequence[float],
    mediated: Sequence[float],
    *,
    seed: int = 0,
    samples: int = 2000,
) -> dict[str, float | int]:
    if len(baseline) != len(mediated) or not baseline:
        raise ValueError("paired samples must be non-empty and equal length")
    if samples < 100:
        raise ValueError("samples must be >= 100")
    deltas = [b - a for a, b in zip(baseline, mediated, strict=True)]
    rng = random.Random(seed)
    boot = [
        sum(rng.choice(deltas) for _ in deltas) / len(deltas) for _ in range(samples)
    ]
    low, high = confidence_interval(boot)
    return {
        "estimate": sum(deltas) / len(deltas),
        "ci_low": low,
        "ci_high": high,
        "samples": samples,
        "seed": seed,
    }


def reliability_bins(
    labels: Sequence[bool | int], probabilities: Sequence[float], bins: int = 10
) -> list[dict[str, float | int]]:
    if len(labels) != len(probabilities) or not labels or bins < 2:
        raise ValueError("labels/probabilities must be non-empty and bins must be >= 2")
    _validate_probabilities(probabilities)
    output: list[dict[str, float | int]] = []
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        selected = [
            (bool(label), probability)
            for label, probability in zip(labels, probabilities, strict=True)
            if lower <= probability < upper
            or (index == bins - 1 and probability == upper)
        ]
        if selected:
            output.append(
                {
                    "bin": index,
                    "count": len(selected),
                    "mean_confidence": sum(p for _, p in selected) / len(selected),
                    "empirical_frequency": sum(float(label) for label, _ in selected)
                    / len(selected),
                }
            )
    return output


def selective_risk(
    labels: Sequence[bool | int], probabilities: Sequence[float], coverage: float
) -> dict[str, float]:
    if len(labels) != len(probabilities) or not labels or not 0.0 < coverage <= 1.0:
        raise ValueError(
            "labels/probabilities must be non-empty and coverage must be in (0, 1]"
        )
    count = max(1, math.ceil(len(labels) * coverage))
    ranked = sorted(
        zip(labels, probabilities, strict=True),
        key=lambda pair: abs(pair[1] - 0.5),
        reverse=True,
    )[:count]
    risk = (
        sum(float(bool(label) != (probability >= 0.5)) for label, probability in ranked)
        / count
    )
    return {"coverage": count / len(labels), "risk": risk}


__all__ = [
    "brier_score",
    "confidence_interval",
    "expected_calibration_error",
    "log_loss",
    "paired_bootstrap_delta",
    "reliability_bins",
    "selective_risk",
]
