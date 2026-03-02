"""
Inference Optimizer

Main inference optimization engine with caching and batching.
"""

import threading
import time
from collections.abc import Callable
from typing import Any

from .batcher import RequestBatcher
from .cache import InferenceCache
from .models import InferenceResult, InferenceStats, OptimizationConfig


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
        model_fn: Callable[[list[Any]], list[Any]],
        config: OptimizationConfig | None = None,
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
        self._latencies: list[float] = []
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

    def _batch_process(self, inputs: list[Any]) -> list[Any]:
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

    def infer_batch(self, inputs: list[Any]) -> list[InferenceResult]:
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
