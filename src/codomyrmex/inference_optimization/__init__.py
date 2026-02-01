"""
Inference Optimization Module

Model optimization techniques including quantization and batching.
"""

__version__ = "0.1.0"

import time
import threading
from typing import Optional, List, Dict, Any, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future
import queue


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


class InferenceCache:
    """
    Cache for inference results.
    
    Usage:
        cache = InferenceCache(max_size=1000)
        
        cache.put("key1", result1)
        result = cache.get("key1")
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}
        self._access_order: List[str] = []
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached result."""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                return self._cache[key]
        return None
    
    def put(self, key: str, value: Any) -> None:
        """Cache a result."""
        with self._lock:
            if key in self._cache:
                self._access_order.remove(key)
            elif len(self._cache) >= self.max_size:
                # Evict LRU
                lru_key = self._access_order.pop(0)
                del self._cache[lru_key]
            
            self._cache[key] = value
            self._access_order.append(key)
    
    def contains(self, key: str) -> bool:
        """Check if key is cached."""
        return key in self._cache
    
    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    @property
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)


class RequestBatcher(Generic[T]):
    """
    Batches inference requests for efficiency.
    
    Usage:
        batcher = RequestBatcher(
            max_batch_size=16,
            timeout_ms=50,
            processor=batch_inference_fn,
        )
        
        # Sync usage
        result = batcher.submit_sync(input_data)
        
        # Async usage
        future = batcher.submit_async(input_data)
        result = future.result()
    """
    
    def __init__(
        self,
        max_batch_size: int = 32,
        timeout_ms: float = 100.0,
        processor: Optional[Callable[[List[T]], List[Any]]] = None,
    ):
        self.max_batch_size = max_batch_size
        self.timeout_ms = timeout_ms
        self.processor = processor
        
        self._queue: queue.Queue = queue.Queue()
        self._pending: Dict[str, Future] = {}
        self._counter = 0
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # Stats
        self._total_requests = 0
        self._total_batches = 0
        self._batch_sizes: List[int] = []
    
    def start(self) -> None:
        """Start the batching thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the batching thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def _get_request_id(self) -> str:
        """Generate unique request ID."""
        with self._lock:
            self._counter += 1
            return f"req_{self._counter}"
    
    def submit_sync(self, input_data: T, timeout: float = 30.0) -> Any:
        """Submit request and wait for result."""
        request_id = self._get_request_id()
        future: Future = Future()
        
        self._queue.put((request_id, input_data, future))
        self._total_requests += 1
        
        return future.result(timeout=timeout)
    
    def submit_async(self, input_data: T) -> Future:
        """Submit request and return future."""
        request_id = self._get_request_id()
        future: Future = Future()
        
        self._queue.put((request_id, input_data, future))
        self._total_requests += 1
        
        return future
    
    def _process_loop(self) -> None:
        """Main processing loop."""
        while self._running:
            batch = self._collect_batch()
            if batch:
                self._process_batch(batch)
    
    def _collect_batch(self) -> List[tuple]:
        """Collect a batch of requests."""
        batch = []
        deadline = time.time() + (self.timeout_ms / 1000)
        
        while len(batch) < self.max_batch_size:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            
            try:
                item = self._queue.get(timeout=remaining)
                batch.append(item)
            except queue.Empty:
                break
        
        return batch
    
    def _process_batch(self, batch: List[tuple]) -> None:
        """Process a collected batch."""
        if not batch or not self.processor:
            return
        
        request_ids = [item[0] for item in batch]
        inputs = [item[1] for item in batch]
        futures = [item[2] for item in batch]
        
        try:
            outputs = self.processor(inputs)
            
            for i, output in enumerate(outputs):
                futures[i].set_result(output)
            
            self._total_batches += 1
            self._batch_sizes.append(len(batch))
            
        except Exception as e:
            for future in futures:
                future.set_exception(e)
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get batching statistics."""
        avg_batch = (
            sum(self._batch_sizes) / len(self._batch_sizes)
            if self._batch_sizes else 0
        )
        return {
            "total_requests": self._total_requests,
            "total_batches": self._total_batches,
            "avg_batch_size": avg_batch,
        }


class InferenceOptimizer:
    """
    Main inference optimization engine.
    
    Usage:
        def model_fn(inputs: List[str]) -> List[str]:
            return [llm.complete(x) for x in inputs]
        
        optimizer = InferenceOptimizer(
            model_fn=model_fn,
            config=OptimizationConfig(
                max_batch_size=16,
                enable_caching=True,
            ),
        )
        
        result = optimizer.infer("Hello, world!")
    """
    
    def __init__(
        self,
        model_fn: Callable[[List[Any]], List[Any]],
        config: Optional[OptimizationConfig] = None,
    ):
        self.model_fn = model_fn
        self.config = config or OptimizationConfig()
        
        self._cache = InferenceCache(max_size=self.config.cache_max_size)
        self._batcher = RequestBatcher(
            max_batch_size=self.config.max_batch_size,
            timeout_ms=self.config.batch_timeout_ms,
            processor=self._batch_process,
        )
        
        self._stats = InferenceStats()
        self._latencies: List[float] = []
        self._lock = threading.Lock()
    
    def start(self) -> None:
        """Start the optimizer."""
        self._batcher.start()
    
    def stop(self) -> None:
        """Stop the optimizer."""
        self._batcher.stop()
    
    def _get_cache_key(self, input_data: Any) -> str:
        """Generate cache key for input."""
        if isinstance(input_data, str):
            return input_data
        return str(hash(str(input_data)))
    
    def _batch_process(self, inputs: List[Any]) -> List[Any]:
        """Process a batch of inputs."""
        return self.model_fn(inputs)
    
    def infer(self, input_data: Any, use_cache: bool = True) -> InferenceResult:
        """
        Run inference on input data.
        
        Args:
            input_data: The input to process
            use_cache: Whether to use caching
            
        Returns:
            InferenceResult with output and metadata
        """
        start_time = time.time()
        cache_key = self._get_cache_key(input_data)
        
        # Check cache
        if use_cache and self.config.enable_caching:
            cached = self._cache.get(cache_key)
            if cached is not None:
                latency_ms = (time.time() - start_time) * 1000
                self._stats.cache_hits += 1
                
                return InferenceResult(
                    request_id="cached",
                    output=cached,
                    latency_ms=latency_ms,
                    from_cache=True,
                )
            else:
                self._stats.cache_misses += 1
        
        # Process (direct call for simplicity)
        output = self.model_fn([input_data])[0]
        latency_ms = (time.time() - start_time) * 1000
        
        # Cache result
        if use_cache and self.config.enable_caching:
            self._cache.put(cache_key, output)
        
        # Update stats
        with self._lock:
            self._stats.total_requests += 1
            self._latencies.append(latency_ms)
        
        return InferenceResult(
            request_id="direct",
            output=output,
            latency_ms=latency_ms,
        )
    
    def infer_batch(self, inputs: List[Any]) -> List[InferenceResult]:
        """Run inference on a batch of inputs."""
        results = []
        start_time = time.time()
        
        # Process batch
        outputs = self.model_fn(inputs)
        total_latency = (time.time() - start_time) * 1000
        per_item_latency = total_latency / len(inputs)
        
        for i, output in enumerate(outputs):
            results.append(InferenceResult(
                request_id=f"batch_{i}",
                output=output,
                latency_ms=per_item_latency,
                batch_size=len(inputs),
            ))
        
        with self._lock:
            self._stats.total_requests += len(inputs)
            self._stats.total_batches += 1
        
        return results
    
    @property
    def stats(self) -> InferenceStats:
        """Get inference statistics."""
        stats = InferenceStats(
            total_requests=self._stats.total_requests,
            total_batches=self._stats.total_batches,
            cache_hits=self._stats.cache_hits,
            cache_misses=self._stats.cache_misses,
        )
        
        if self._latencies:
            stats.avg_latency_ms = sum(self._latencies) / len(self._latencies)
        
        return stats
    
    def clear_cache(self) -> None:
        """Clear the inference cache."""
        self._cache.clear()


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
