"""
Inference Optimization Module

Model optimization techniques including quantization and batching.
"""

__version__ = "0.1.0"

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

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

def cli_commands():
    """Return CLI commands for the inference_optimization module."""
    return {
        "strategies": {
            "help": "List available optimization strategies",
            "handler": lambda **kwargs: print(
                "Inference Optimization Strategies\n"
                f"  Quantization types: {', '.join(qt.value if hasattr(qt, 'value') else str(qt) for qt in QuantizationType)}\n"
                f"  Batching strategies: {', '.join(bs.value if hasattr(bs, 'value') else str(bs) for bs in BatchingStrategy)}\n"
                "  Components: InferenceCache, RequestBatcher, InferenceOptimizer"
            ),
        },
        "benchmark": {
            "help": "Run inference optimization benchmark",
            "handler": lambda **kwargs: print(
                "Inference Optimization Benchmark\n"
                "  Use InferenceOptimizer to run benchmarks programmatically.\n"
                "  Configure via OptimizationConfig for quantization and batching settings."
            ),
        },
    }


__all__ = [
    # CLI integration
    "cli_commands",
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
