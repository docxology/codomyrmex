"""
Unit tests for model_ops.optimization — Zero-Mock compliant.

Covers: QuantizationType, BatchingStrategy, OptimizationConfig,
InferenceStats, InferenceRequest, InferenceResult, InferenceCache,
InferenceOptimizer (infer, infer_batch, stats, clear_cache).
"""

import time

import pytest

from codomyrmex.model_ops.optimization.cache import InferenceCache
from codomyrmex.model_ops.optimization.models import (
    BatchingStrategy,
    InferenceRequest,
    InferenceResult,
    InferenceStats,
    OptimizationConfig,
    QuantizationType,
)
from codomyrmex.model_ops.optimization.optimizer import InferenceOptimizer

# ── Enum tests ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEnums:
    def test_quantization_types(self):
        assert QuantizationType.FP32.value == "fp32"
        assert QuantizationType.FP16.value == "fp16"
        assert QuantizationType.INT8.value == "int8"
        assert QuantizationType.INT4.value == "int4"

    def test_batching_strategies(self):
        assert BatchingStrategy.FIXED.value == "fixed"
        assert BatchingStrategy.DYNAMIC.value == "dynamic"
        assert BatchingStrategy.ADAPTIVE.value == "adaptive"


# ── OptimizationConfig ────────────────────────────────────────────────


@pytest.mark.unit
class TestOptimizationConfig:
    def test_defaults(self):
        c = OptimizationConfig()
        assert c.quantization == QuantizationType.FP32
        assert c.max_batch_size == 32
        assert c.batch_timeout_ms == 100.0
        assert c.enable_caching is True
        assert c.cache_max_size == 1000

    def test_custom_config(self):
        c = OptimizationConfig(
            quantization=QuantizationType.INT8,
            max_batch_size=8,
            enable_caching=False,
        )
        assert c.quantization == QuantizationType.INT8
        assert c.max_batch_size == 8
        assert c.enable_caching is False


# ── InferenceStats ────────────────────────────────────────────────────


@pytest.mark.unit
class TestInferenceStats:
    def test_defaults(self):
        s = InferenceStats()
        assert s.total_requests == 0
        assert s.cache_hits == 0
        assert s.cache_misses == 0

    def test_cache_hit_rate_zero_when_no_requests(self):
        s = InferenceStats()
        assert s.cache_hit_rate == 0.0

    def test_cache_hit_rate_calculation(self):
        s = InferenceStats(cache_hits=3, cache_misses=1)
        assert s.cache_hit_rate == 0.75

    def test_cache_hit_rate_all_hits(self):
        s = InferenceStats(cache_hits=10, cache_misses=0)
        assert s.cache_hit_rate == 1.0


# ── InferenceRequest ──────────────────────────────────────────────────


@pytest.mark.unit
class TestInferenceRequest:
    def test_fields(self):
        req = InferenceRequest(id="r1", input_data="hello")
        assert req.id == "r1"
        assert req.input_data == "hello"
        assert req.priority == 0

    def test_age_ms_is_positive(self):
        req = InferenceRequest(id="r1", input_data="data")
        time.sleep(0.001)
        assert req.age_ms > 0


# ── InferenceResult ───────────────────────────────────────────────────


@pytest.mark.unit
class TestInferenceResult:
    def test_fields(self):
        result = InferenceResult(
            request_id="r1",
            output="response",
            latency_ms=12.5,
        )
        assert result.request_id == "r1"
        assert result.output == "response"
        assert result.latency_ms == 12.5
        assert result.from_cache is False
        assert result.batch_size == 1

    def test_from_cache_flag(self):
        result = InferenceResult(
            request_id="cached",
            output="cached_output",
            latency_ms=0.1,
            from_cache=True,
        )
        assert result.from_cache is True


# ── InferenceCache ────────────────────────────────────────────────────


@pytest.mark.unit
class TestInferenceCache:
    def test_initial_size_zero(self):
        cache = InferenceCache()
        assert cache.size == 0

    def test_put_and_get(self):
        cache = InferenceCache()
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_returns_none(self):
        cache = InferenceCache()
        assert cache.get("nonexistent") is None

    def test_contains(self):
        cache = InferenceCache()
        assert not cache.contains("k1")
        cache.put("k1", "v1")
        assert cache.contains("k1")

    def test_size_after_puts(self):
        cache = InferenceCache()
        cache.put("a", 1)
        cache.put("b", 2)
        assert cache.size == 2

    def test_clear_removes_all(self):
        cache = InferenceCache()
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()
        assert cache.size == 0
        assert cache.get("a") is None

    def test_lru_eviction(self):
        cache = InferenceCache(max_size=2)
        cache.put("a", 1)
        cache.put("b", 2)
        # Access "a" to make "b" LRU
        cache.get("a")
        # Adding "c" should evict "b" (LRU)
        cache.put("c", 3)
        assert cache.get("c") == 3
        assert cache.get("a") == 1
        assert cache.get("b") is None

    def test_overwrite_existing_key(self):
        cache = InferenceCache()
        cache.put("key", "old")
        cache.put("key", "new")
        assert cache.get("key") == "new"
        assert cache.size == 1

    def test_put_updates_access_order(self):
        cache = InferenceCache(max_size=2)
        cache.put("a", 1)
        cache.put("b", 2)
        # Overwrite "a" — should make "a" most recently used
        cache.put("a", 99)
        # Now "b" is LRU, adding "c" evicts "b"
        cache.put("c", 3)
        assert cache.get("a") == 99
        assert cache.get("c") == 3
        assert cache.get("b") is None


# ── InferenceOptimizer ────────────────────────────────────────────────


def _echo_model(inputs):
    """Identity model: returns inputs unchanged."""
    return inputs


def _upper_model(inputs):
    """Uppercase model."""
    return [s.upper() for s in inputs]


@pytest.mark.unit
class TestInferenceOptimizer:
    def test_basic_infer(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        result = opt.infer("hello")
        assert result.output == "hello"
        assert result.from_cache is False

    def test_infer_returns_inference_result(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        result = opt.infer("test")
        assert isinstance(result, InferenceResult)
        assert result.latency_ms >= 0

    def test_cache_hit_on_second_call(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        opt.infer("hello")
        result2 = opt.infer("hello")
        assert result2.from_cache is True

    def test_cache_miss_different_input(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        opt.infer("hello")
        result = opt.infer("world")
        assert result.from_cache is False

    def test_no_cache_when_disabled(self):
        config = OptimizationConfig(enable_caching=False)
        opt = InferenceOptimizer(model_fn=_echo_model, config=config)
        opt.infer("hello")
        result2 = opt.infer("hello")
        assert result2.from_cache is False

    def test_infer_no_cache_flag(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        opt.infer("hello")
        result = opt.infer("hello", use_cache=False)
        assert result.from_cache is False

    def test_infer_batch(self):
        opt = InferenceOptimizer(model_fn=_upper_model)
        results = opt.infer_batch(["hello", "world"])
        assert len(results) == 2
        assert results[0].output == "HELLO"
        assert results[1].output == "WORLD"

    def test_infer_batch_batch_size_set(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        results = opt.infer_batch(["a", "b", "c"])
        for r in results:
            assert r.batch_size == 3

    def test_stats_initial(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        s = opt.stats
        assert s.total_requests == 0

    def test_stats_after_infer(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        opt.infer("hello")
        s = opt.stats
        assert s.total_requests == 1

    def test_stats_cache_tracking(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        opt.infer("hello")  # cache miss
        opt.infer("hello")  # cache hit
        s = opt.stats
        assert s.cache_hits == 1
        assert s.cache_misses == 1

    def test_stats_avg_latency(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        opt.infer("x")
        s = opt.stats
        assert s.avg_latency_ms >= 0

    def test_clear_cache(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        opt.infer("hello")
        opt.clear_cache()
        # After clear, next call should be a cache miss
        result = opt.infer("hello")
        assert result.from_cache is False

    def test_get_cache_key_string(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        assert opt._get_cache_key("hello") == "hello"

    def test_get_cache_key_non_string(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        key = opt._get_cache_key({"data": 42})
        assert isinstance(key, str)

    def test_start_stop(self):
        opt = InferenceOptimizer(model_fn=_echo_model)
        opt.start()
        opt.stop()  # Should not raise
