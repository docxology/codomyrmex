"""
Inference Optimization Module

Model optimization techniques including quantization and batching.
"""

__version__ = "0.1.0"

from .models import (
    BatchingStrategy,
    InferenceRequest,
    InferenceResult,
    InferenceStats,
    OptimizationConfig,
    QuantizationType,
)
from .cache import InferenceCache
from .batcher import RequestBatcher
from .optimizer import InferenceOptimizer

__all__ = [
    # Enums
    "QuantizationType",
    "BatchingStrategy",
    # Data classes
    "OptimizationConfig",
    "InferenceStats",
    "InferenceRequest",
    "InferenceResult",
    # Components
    "InferenceCache",
    "RequestBatcher",
    # Core
    "InferenceOptimizer",
]
