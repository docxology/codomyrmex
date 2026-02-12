"""Fitness functions for memes and memeplexes."""

from __future__ import annotations

import math
from typing import List

from codomyrmex.meme.memetics.models import Meme, Memeplex


def virality_score(meme: Meme, network_size: int = 1000) -> float:
    """Estimate virality potential of a meme.

    Combines fecundity with content characteristics (length penalty,
    simplicity bonus) and network scaling.

    Args:
        meme: The meme to score.
        network_size: Size of the target network (scales logarithmically).

    Returns:
        Virality score (0–1).
    """
    # Shorter content is more shareable
    word_count = len(meme.content.split())
    brevity_bonus = 1.0 / (1.0 + math.log1p(word_count))

    # Network effect: log scaling
    network_factor = math.log1p(network_size) / math.log1p(10000)
    network_factor = min(1.0, network_factor)

    raw = meme.fecundity * 0.4 + brevity_bonus * 0.3 + network_factor * 0.3
    return max(0.0, min(1.0, raw))


def robustness_score(memeplex: Memeplex) -> float:
    """Score how robust a memeplex is to perturbation.

    Uses the coefficient of variation of meme fitnesses — higher
    uniformity means higher robustness. Also factors in synergy
    and population size.

    Args:
        memeplex: The memeplex to evaluate.

    Returns:
        Robustness score (0–1).
    """
    if len(memeplex.memes) < 2:
        return memeplex.synergy

    fitnesses = [m.fitness for m in memeplex.memes]
    mean = sum(fitnesses) / len(fitnesses)
    if mean == 0:
        return 0.0

    variance = sum((f - mean) ** 2 for f in fitnesses) / len(fitnesses)
    cv = math.sqrt(variance) / mean  # Coefficient of variation

    uniformity = 1.0 / (1.0 + cv)
    redundancy = min(1.0, len(memeplex.memes) / 10.0)

    return (uniformity * 0.5 + redundancy * 0.2 + memeplex.synergy * 0.3)


def decay_rate(meme: Meme, half_life_days: float = 7.0) -> float:
    """Calculate the expected decay rate of a meme.

    Models memetic decay as exponential, modified by the meme's
    longevity attribute.

    Args:
        meme: The meme to evaluate.
        half_life_days: Base half-life in days before longevity adjustment.

    Returns:
        Decay constant (lambda). Higher = faster decay.
    """
    adjusted_half_life = half_life_days * (1.0 + meme.longevity * 4.0)
    if adjusted_half_life <= 0:
        return float("inf")
    return math.log(2) / adjusted_half_life


def population_fitness_stats(population: List[Meme]) -> dict:
    """Compute summary statistics for a meme population.

    Args:
        population: List of memes.

    Returns:
        Dict with keys: mean, std, min, max, count.
    """
    if not population:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "count": 0}

    fitnesses = [m.fitness for m in population]
    n = len(fitnesses)
    mean = sum(fitnesses) / n
    variance = sum((f - mean) ** 2 for f in fitnesses) / n
    return {
        "mean": mean,
        "std": math.sqrt(variance),
        "min": min(fitnesses),
        "max": max(fitnesses),
        "count": n,
    }
