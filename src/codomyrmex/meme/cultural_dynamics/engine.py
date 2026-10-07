"""CulturalDynamicsEngine — orchestrator for cultural modeling."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from codomyrmex.meme.cultural_dynamics.models import (
    CulturalState,
    FrequencyMap,
    PowerMap,
    Signal,
    Trajectory,
)

if TYPE_CHECKING:
    from codomyrmex.meme.memetics.models import Meme


class CulturalDynamicsEngine:
    """Engine for modeling cultural systems as dynamical systems."""

    def oscillation_spectrum(
        self, time_series: list[CulturalState], dimension: str
    ) -> FrequencyMap:
        """Find the dominant oscillation of a dimension with a discrete Fourier transform.

        The states are treated as evenly spaced samples (their timestamps are
        not used), so frequency is in cycles per sample and period in samples.
        A missing dimension counts as 0.0. The mean is removed, the real FFT
        is taken, and the strongest non-DC bin ``k`` gives
        ``dominant_frequency = k / N``, ``period = N / k`` and
        ``amplitude = 2 * |X_k| / N`` (``|X_k| / N`` for the Nyquist bin).
        A dominant period is only exact when it divides ``N``; otherwise
        energy leaks into neighbouring bins.

        Fewer than two samples, or a constant series, has no oscillation:
        frequency, period and amplitude are all 0.0.
        """
        values = np.array(
            [s.dimensions.get(dimension, 0.0) for s in time_series], dtype=float
        )
        n = values.size
        if n < 2 or np.ptp(values) == 0.0:
            return FrequencyMap(dimension, 0.0, 0.0, 0.0)

        magnitudes = np.abs(np.fft.rfft(values - values.mean()))
        k = int(np.argmax(magnitudes[1:])) + 1
        is_nyquist = n % 2 == 0 and k == n // 2
        amplitude = magnitudes[k] / n if is_nyquist else 2.0 * magnitudes[k] / n

        return FrequencyMap(
            dimension=dimension,
            dominant_frequency=k / n,
            period=n / k,
            amplitude=float(amplitude),
        )

    def zeitgeist_trajectory(self, signals: list[Signal]) -> Trajectory:
        """Aggregate signals into a coherent zeitgeist trajectory."""
        signals.sort(key=lambda x: x.timestamp)
        states = []

        # Simple moving average state construction
        current_dims: dict[str, float] = {}

        for sig in signals:
            curr = current_dims.get(sig.dimension, 0.0)
            # Update via exponential moving average
            alpha = 0.1
            new_val = curr + alpha * (sig.valence * sig.strength - curr)
            current_dims[sig.dimension] = new_val

            states.append(
                CulturalState(dimensions=current_dims.copy(), timestamp=sig.timestamp)
            )

        return Trajectory(states=states)

    def mutation_probability(self, state: CulturalState, perturbation: Meme) -> float:
        """Calculate probability of cultural mutation given current state.

        High 'energy' (tension) increases mutation probability.
        """
        # Meme compatibility check placeholder
        return min(0.9, state.energy * 0.5 + 0.1)

    def power_topology(self, nodes: list[str], interactions: list[tuple]) -> PowerMap:
        """Map power dynamics from interaction graph."""
        # Simple degree centrality placeholder
        scores = dict.fromkeys(nodes, 0.1)
        for src, _dst in interactions:
            scores[src] = scores.get(src, 0.1) + 0.05

        return PowerMap(nodes=nodes, centrality_scores=scores)
