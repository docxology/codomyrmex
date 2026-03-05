"""
codomyrmex.meme.memetics — Core Memetic Engine.

Data structures and algorithms for modeling memes as discrete replicable
information units with fitness, mutation rates, and transmission vectors.
"""

from codomyrmex.meme.memetics.engine import MemeticEngine
from codomyrmex.meme.memetics.fitness import (
    decay_rate,
    robustness_score,
    virality_score,
)
from codomyrmex.meme.memetics.models import (
    FitnessMap,
    Meme,
    Memeplex,
    MemeticCode,
)
from codomyrmex.meme.memetics.mutation import (
    recombine,
    semantic_drift,
    splice,
)

__all__ = [
    "FitnessMap",
    "Meme",
    "Memeplex",
    "MemeticCode",
    "MemeticEngine",
    "decay_rate",
    "recombine",
    "robustness_score",
    "semantic_drift",
    "splice",
    "virality_score",
]
