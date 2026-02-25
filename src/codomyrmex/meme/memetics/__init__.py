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
    "Meme", "Memeplex", "MemeticCode", "FitnessMap",
    "MemeticEngine",
    "semantic_drift", "recombine", "splice",
    "virality_score", "robustness_score", "decay_rate",
]
