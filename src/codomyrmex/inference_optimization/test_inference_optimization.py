"""
Tests for Inference Optimization Module
"""

import pytest
from codomyrmex.inference_optimization import (
    QuantizationType,
    OptimizationConfig,
    InferenceStats,
    InferenceResult,
    InferenceCache,
    RequestBatcher,
    InferenceOptimizer,
)


class TestInferenceCache:
    """Tests for InferenceCache."""
    
    def test_put_and_get(self):
        """Should store and retrieve."""
        cache = InferenceCache(max_size=10)
        cache.put("key1", "value1")
        
        assert cache.get("key1") == "value1"
        assert cache.get("missing") is None
    
    def test_lru_eviction(self):
        """Should evict LRU items."""
        cache = InferenceCache(max_size=2)
        cache.put("k1", "v1")
        cache.put("k2", "v2")
        cache.put("k3", "v3")  # This should evict k1
        
        assert cache.get("k1") is None
        assert cache.get("k2") == "v2"
        assert cache.get("k3") == "v3"
    
    def test_size(self):
        """Should track size."""
        cache = InferenceCache(max_size=10)
        assert cache.size == 0
        
        cache.put("k1", "v1")
        assert cache.size == 1
    
    def test_clear(self):
        """Should clear cache."""
        cache = InferenceCache()
        cache.put("k1", "v1")
        cache.clear()
        
        assert cache.size == 0


class TestInferenceOptimizer:
    """Tests for InferenceOptimizer."""
    
    def test_infer(self):
        """Should run inference."""
        def model_fn(inputs):
            return [f"output_{x}" for x in inputs]
        
        optimizer = InferenceOptimizer(model_fn=model_fn)
        result = optimizer.infer("test")
        
        assert result.output == "output_test"
        assert isinstance(result, InferenceResult)
    
    def test_caching(self):
        """Should cache results."""
        call_count = 0
        
        def model_fn(inputs):
            nonlocal call_count
            call_count += 1
            return [f"output_{x}" for x in inputs]
        
        optimizer = InferenceOptimizer(
            model_fn=model_fn,
            config=OptimizationConfig(enable_caching=True),
        )
        
        # First call - cache miss
        result1 = optimizer.infer("test")
        assert call_count == 1
        assert result1.from_cache is False
        
        # Second call - cache hit
        result2 = optimizer.infer("test")
        assert call_count == 1  # No new call
        assert result2.from_cache is True
    
    def test_infer_batch(self):
        """Should process batch."""
        def model_fn(inputs):
            return [f"out_{x}" for x in inputs]
        
        optimizer = InferenceOptimizer(model_fn=model_fn)
        results = optimizer.infer_batch(["a", "b", "c"])
        
        assert len(results) == 3
        assert results[0].output == "out_a"
        assert results[0].batch_size == 3
    
    def test_stats(self):
        """Should track stats."""
        def model_fn(inputs):
            return inputs
        
        optimizer = InferenceOptimizer(model_fn=model_fn)
        optimizer.infer("a")
        optimizer.infer("b")
        
        stats = optimizer.stats
        assert stats.total_requests == 2
    
    def test_clear_cache(self):
        """Should clear cache."""
        def model_fn(inputs):
            return inputs
        
        optimizer = InferenceOptimizer(model_fn=model_fn)
        optimizer.infer("test")
        
        optimizer.clear_cache()
        assert optimizer._cache.size == 0


class TestOptimizationConfig:
    """Tests for OptimizationConfig."""
    
    def test_defaults(self):
        """Should have defaults."""
        config = OptimizationConfig()
        assert config.quantization == QuantizationType.FP32
        assert config.max_batch_size == 32


class TestInferenceStats:
    """Tests for InferenceStats."""
    
    def test_cache_hit_rate(self):
        """Should calculate cache hit rate."""
        stats = InferenceStats(cache_hits=80, cache_misses=20)
        assert stats.cache_hit_rate == 0.8
    
    def test_zero_division(self):
        """Should handle zero."""
        stats = InferenceStats()
        assert stats.cache_hit_rate == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
