"""
codomyrmex.meme.memetics — Core Memetic Engine.

Data structures and algorithms for modeling memes as discrete replicable
information units with fitness, mutation rates, and transmission vectors.
"""

from codomyrmex.meme.memetics.models import (
    Meme,
    Memeplex,
    MemeticCode,
    FitnessMap,
)
from codomyrmex.meme.memetics.engine import MemeticEngine
from codomyrmex.meme.memetics.mutation import (
    semantic_drift,
    recombine,
    splice,
)
from codomyrmex.meme.memetics.fitness import (
    virality_score,
    robustness_score,
    decay_rate,
)

__all__ = [
    "Meme", "Memeplex", "MemeticCode", "FitnessMap",
    "MemeticEngine",
    "semantic_drift", "recombine", "splice",
    "virality_score", "robustness_score", "decay_rate",
]
