"""
Inference Optimization Models

Data classes and enums for inference optimization.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar('T')


class QuantizationType(Enum):
    """Types of quantization."""
    FP32 = "fp32"
    FP16 = "fp16"
    INT8 = "int8"
    INT4 = "int4"


class BatchingStrategy(Enum):
    """Strategies for batching requests."""
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    ADAPTIVE = "adaptive"


@dataclass
class OptimizationConfig:
    """Configuration for inference optimization."""
    quantization: QuantizationType = QuantizationType.FP32
    max_batch_size: int = 32
    batch_timeout_ms: float = 100.0
    enable_caching: bool = True
    cache_max_size: int = 1000
    num_workers: int = 4


@dataclass
class InferenceStats:
    """Statistics for inference performance."""
    total_requests: int = 0
    total_batches: int = 0
    avg_batch_size: float = 0.0
    avg_latency_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0

    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


@dataclass
class InferenceRequest(Generic[T]):
    """A single inference request."""
    id: str
    input_data: T
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def age_ms(self) -> float:
        """Get request age in milliseconds."""
        return (datetime.now() - self.created_at).total_seconds() * 1000


@dataclass
class InferenceResult(Generic[T]):
    """Result of an inference request."""
    request_id: str
    output: T
    latency_ms: float
    from_cache: bool = False
    batch_size: int = 1
