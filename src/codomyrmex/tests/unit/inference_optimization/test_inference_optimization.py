"""Unit tests for inference_optimization module."""
import time

import pytest


@pytest.mark.unit
class TestInferenceOptimizationImports:
    """Test suite for inference_optimization module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex.model_ops import optimization as inference_optimization
        assert hasattr(inference_optimization, '__name__')

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.model_ops.optimization import __all__
        expected_exports = [
            "QuantizationType",
            "BatchingStrategy",
            "OptimizationConfig",
            "InferenceStats",
            "InferenceRequest",
            "InferenceResult",
            "InferenceCache",
            "RequestBatcher",
            "InferenceOptimizer",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestQuantizationType:
    """Test suite for QuantizationType enum."""

    def test_quantization_type_values(self):
        """Verify all quantization types are available."""
        from codomyrmex.model_ops.optimization import QuantizationType

        assert QuantizationType.FP32.value == "fp32"
        assert QuantizationType.FP16.value == "fp16"
        assert QuantizationType.INT8.value == "int8"
        assert QuantizationType.INT4.value == "int4"


@pytest.mark.unit
class TestBatchingStrategy:
    """Test suite for BatchingStrategy enum."""

    def test_batching_strategy_values(self):
        """Verify all batching strategies are available."""
        from codomyrmex.model_ops.optimization import BatchingStrategy

        assert BatchingStrategy.FIXED.value == "fixed"
        assert BatchingStrategy.DYNAMIC.value == "dynamic"
        assert BatchingStrategy.ADAPTIVE.value == "adaptive"


@pytest.mark.unit
class TestOptimizationConfig:
    """Test suite for OptimizationConfig dataclass."""

    def test_config_defaults(self):
        """Verify default configuration values."""
        from codomyrmex.model_ops.optimization import (
            OptimizationConfig,
            QuantizationType,
        )

        config = OptimizationConfig()

        assert config.quantization == QuantizationType.FP32
        assert config.max_batch_size == 32
        assert config.batch_timeout_ms == 100.0
        assert config.enable_caching is True
        assert config.cache_max_size == 1000
        assert config.num_workers == 4

    def test_config_custom_values(self):
        """Verify custom configuration values."""
        from codomyrmex.model_ops.optimization import (
            OptimizationConfig,
            QuantizationType,
        )

        config = OptimizationConfig(
            quantization=QuantizationType.INT8,
            max_batch_size=64,
            enable_caching=False,
        )

        assert config.quantization == QuantizationType.INT8
        assert config.max_batch_size == 64
        assert config.enable_caching is False


@pytest.mark.unit
class TestInferenceStats:
    """Test suite for InferenceStats dataclass."""

    def test_stats_defaults(self):
        """Verify default stats values."""
        from codomyrmex.model_ops.optimization import InferenceStats

        stats = InferenceStats()

        assert stats.total_requests == 0
        assert stats.total_batches == 0
        assert stats.avg_batch_size == 0.0
        assert stats.avg_latency_ms == 0.0

    def test_stats_cache_hit_rate(self):
        """Verify cache hit rate calculation."""
        from codomyrmex.model_ops.optimization import InferenceStats

        stats = InferenceStats(cache_hits=80, cache_misses=20)
        assert stats.cache_hit_rate == 0.8

        empty_stats = InferenceStats()
        assert empty_stats.cache_hit_rate == 0.0


@pytest.mark.unit
class TestInferenceRequest:
    """Test suite for InferenceRequest dataclass."""

    def test_request_creation(self):
        """Verify request can be created."""
        from codomyrmex.model_ops.optimization import InferenceRequest

        request = InferenceRequest(
            id="req_1",
            input_data="Hello, world!",
            priority=1,
        )

        assert request.id == "req_1"
        assert request.input_data == "Hello, world!"
        assert request.priority == 1

    def test_request_age(self):
        """Verify request age calculation."""
        from codomyrmex.model_ops.optimization import InferenceRequest

        request = InferenceRequest(id="test", input_data="data")
        time.sleep(0.01)  # Small delay

        assert request.age_ms > 0


@pytest.mark.unit
class TestInferenceResult:
    """Test suite for InferenceResult dataclass."""

    def test_result_creation(self):
        """Verify result can be created."""
        from codomyrmex.model_ops.optimization import InferenceResult

        result = InferenceResult(
            request_id="req_1",
            output="response",
            latency_ms=50.0,
        )

        assert result.request_id == "req_1"
        assert result.output == "response"
        assert result.latency_ms == 50.0
        assert result.from_cache is False


@pytest.mark.unit
class TestInferenceCache:
    """Test suite for InferenceCache."""

    def test_cache_put_and_get(self):
        """Verify cache put and get operations."""
        from codomyrmex.model_ops.optimization import InferenceCache

        cache = InferenceCache(max_size=100)

        cache.put("key1", "value1")
        result = cache.get("key1")

        assert result == "value1"

    def test_cache_miss(self):
        """Verify cache miss returns None."""
        from codomyrmex.model_ops.optimization import InferenceCache

        cache = InferenceCache()
        result = cache.get("nonexistent")

        assert result is None

    def test_cache_lru_eviction(self):
        """Verify LRU eviction when cache is full."""
        from codomyrmex.model_ops.optimization import InferenceCache

        cache = InferenceCache(max_size=2)

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_size_property(self):
        """Verify cache size tracking."""
        from codomyrmex.model_ops.optimization import InferenceCache

        cache = InferenceCache(max_size=10)

        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)

        assert cache.size == 3

    def test_cache_clear(self):
        """Verify cache clearing."""
        from codomyrmex.model_ops.optimization import InferenceCache

        cache = InferenceCache()
        cache.put("key", "value")
        cache.clear()

        assert cache.size == 0
        assert cache.get("key") is None

    def test_cache_contains(self):
        """Verify contains check."""
        from codomyrmex.model_ops.optimization import InferenceCache

        cache = InferenceCache()
        cache.put("exists", "value")

        assert cache.contains("exists") is True
        assert cache.contains("missing") is False


@pytest.mark.unit
class TestRequestBatcher:
    """Test suite for RequestBatcher."""

    def test_batcher_creation(self):
        """Verify batcher can be created."""
        from codomyrmex.model_ops.optimization import RequestBatcher

        batcher = RequestBatcher(
            max_batch_size=16,
            timeout_ms=50.0,
        )

        assert batcher.max_batch_size == 16
        assert batcher.timeout_ms == 50.0

    def test_batcher_stats(self):
        """Verify batcher stats initialization."""
        from codomyrmex.model_ops.optimization import RequestBatcher

        batcher = RequestBatcher()
        stats = batcher.stats

        assert stats["total_requests"] == 0
        assert stats["total_batches"] == 0


@pytest.mark.unit
class TestInferenceOptimizer:
    """Test suite for InferenceOptimizer."""

    def test_optimizer_creation(self):
        """Verify optimizer can be created."""
        from codomyrmex.model_ops.optimization import InferenceOptimizer

        def simple_model(inputs):
            return [f"output_{x}" for x in inputs]

        optimizer = InferenceOptimizer(model_fn=simple_model)

        assert optimizer.model_fn is simple_model

    def test_optimizer_infer_single(self):
        """Verify single inference."""
        from codomyrmex.model_ops.optimization import InferenceOptimizer

        def echo_model(inputs):
            return inputs

        optimizer = InferenceOptimizer(model_fn=echo_model)
        result = optimizer.infer("test_input")

        assert result.output == "test_input"
        assert result.latency_ms > 0

    def test_optimizer_caching(self):
        """Verify caching behavior."""
        from codomyrmex.model_ops.optimization import (
            InferenceOptimizer,
            OptimizationConfig,
        )

        call_count = [0]

        def counting_model(inputs):
            call_count[0] += 1
            return [f"result_{x}" for x in inputs]

        config = OptimizationConfig(enable_caching=True)
        optimizer = InferenceOptimizer(model_fn=counting_model, config=config)

        # First call
        result1 = optimizer.infer("same_input")
        # Second call should be cached
        result2 = optimizer.infer("same_input")

        assert result1.output == result2.output
        assert result2.from_cache is True
        assert call_count[0] == 1  # Model only called once

    def test_optimizer_infer_batch(self):
        """Verify batch inference."""
        from codomyrmex.model_ops.optimization import InferenceOptimizer

        def batch_model(inputs):
            return [x.upper() for x in inputs]

        optimizer = InferenceOptimizer(model_fn=batch_model)
        results = optimizer.infer_batch(["hello", "world"])

        assert len(results) == 2
        assert results[0].output == "HELLO"
        assert results[1].output == "WORLD"
        assert results[0].batch_size == 2

    def test_optimizer_stats(self):
        """Verify stats tracking."""
        from codomyrmex.model_ops.optimization import InferenceOptimizer

        def simple_model(inputs):
            return inputs

        optimizer = InferenceOptimizer(model_fn=simple_model)
        optimizer.infer("test1", use_cache=False)
        optimizer.infer("test2", use_cache=False)

        stats = optimizer.stats
        assert stats.total_requests == 2
        assert stats.avg_latency_ms >= 0

    def test_optimizer_clear_cache(self):
        """Verify cache clearing."""
        from codomyrmex.model_ops.optimization import InferenceOptimizer

        def simple_model(inputs):
            return inputs

        optimizer = InferenceOptimizer(model_fn=simple_model)
        optimizer.infer("test")
        optimizer.clear_cache()

        assert optimizer._cache.size == 0
