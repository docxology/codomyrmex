"""
Comprehensive tests for the Performance module.

This module tests all components of the performance optimization system:
- LazyLoader for deferred module imports
- CacheManager for intelligent caching
- PerformanceMonitor for metrics collection
"""

import json
import os

# Removed mock imports to follow TDD principle: no mock methods, always do real data analysis
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.performance.cache_manager import (
    CacheManager,
    cached_function,
    clear_cache,
    get_cache_stats,
)
from codomyrmex.performance.lazy_loader import (
    LazyLoader,
    get_lazy_loader,
    lazy_function,
    lazy_import,
)

# Import PerformanceMonitor with fallback
try:
    from codomyrmex.performance.performance_monitor import (
        PerformanceMetrics,
        PerformanceMonitor,
        clear_performance_metrics,
        get_performance_stats,
        monitor_performance,
        performance_context,
    )
    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PerformanceMonitor = None
    PerformanceMetrics = None
    monitor_performance = None
    performance_context = None
    get_performance_stats = None
    clear_performance_metrics = None
    PERFORMANCE_MONITOR_AVAILABLE = False


class TestLazyLoader:
    """Test cases for LazyLoader functionality."""

    def test_lazy_loader_initialization(self):
        """Test LazyLoader initialization."""
        loader = LazyLoader('json')
        assert loader.module_name == 'json'
        assert loader.package is None
        assert loader._module is None
        assert not loader._loading

    def test_lazy_loader_with_package(self):
        """Test LazyLoader with package parameter."""
        loader = LazyLoader('pathlib', 'pathlib')
        assert loader.module_name == 'pathlib'
        assert loader.package == 'pathlib'

    def test_lazy_loader_repr(self):
        """Test LazyLoader string representation."""
        loader = LazyLoader('json')
        assert 'LazyLoader' in repr(loader)
        assert 'json' in repr(loader)
        assert 'status=unloaded' in repr(loader)

    def test_lazy_loader_getattr_loading(self):
        """Test that LazyLoader loads module on attribute access."""
        loader = LazyLoader('json')
        json_module = loader.dumps  # Access attribute to trigger loading

        # Should return the actual json.dumps function
        assert callable(json_module)
        assert json_module == json.dumps

        # Module should now be loaded
        assert loader._module is not None
        assert 'status=loaded' in repr(loader)

    def test_lazy_loader_getattr_invalid_module(self):
        """Test LazyLoader with invalid module name."""
        loader = LazyLoader('nonexistent_module_xyz')

        with pytest.raises(ImportError):
            _ = loader.some_attribute

    def test_lazy_import_function(self):
        """Test lazy_import function."""
        json_loader = lazy_import('json')
        assert isinstance(json_loader, LazyLoader)
        assert json_loader.module_name == 'json'

        # Test that it works
        result = json_loader.dumps([1, 2, 3])
        assert result == '[1, 2, 3]'

    def test_get_lazy_loader_registry(self):
        """Test lazy loader registry functionality."""
        # Get the same loader multiple times
        loader1 = get_lazy_loader('json')
        loader2 = get_lazy_loader('json')

        assert loader1 is loader2  # Should be the same instance

    def test_lazy_function(self):
        """Test lazy_function decorator."""
        json_dumps = lazy_function('json', 'dumps')

        # Should work like the original function
        result = json_dumps([1, 2, 3])
        assert result == '[1, 2, 3]'

        # Should have proper name attributes
        assert json_dumps.__name__ == 'dumps'
        assert json_dumps.__qualname__ == 'json.dumps'

    def test_pre_configured_lazy_loaders(self):
        """Test pre-configured lazy loaders for common modules."""
        from codomyrmex.performance.lazy_loader import matplotlib, numpy, pandas

        # These should be LazyLoader instances
        assert isinstance(matplotlib, LazyLoader)
        assert isinstance(numpy, LazyLoader)
        assert isinstance(pandas, LazyLoader)

        # Should have correct module names
        assert matplotlib.module_name == 'matplotlib.pyplot'
        assert numpy.module_name == 'numpy'
        assert pandas.module_name == 'pandas'


class TestCacheManager:
    """Test cases for CacheManager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = CacheManager(cache_dir=self.temp_dir, max_memory_items=10)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_manager_initialization(self):
        """Test CacheManager initialization."""
        assert self.cache.cache_dir == Path(self.temp_dir)
        assert self.cache.max_memory_items == 10
        assert self.cache.default_ttl == 3600
        assert isinstance(self.cache._memory_cache, dict)
        assert isinstance(self.cache._access_times, dict)

    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = self.cache._generate_key('test_func', (1, 2), {'a': 1})
        key2 = self.cache._generate_key('test_func', (1, 2), {'a': 1})
        key3 = self.cache._generate_key('test_func', (1, 2), {'a': 2})

        assert key1 == key2  # Same inputs should generate same key
        assert key1 != key3  # Different inputs should generate different keys
        assert len(key1) == 32  # MD5 hash length

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        # Set a value
        self.cache.set('test_key', 'test_value')

        # Get the value
        result = self.cache.get('test_key')
        assert result == 'test_value'

    def test_cache_expiration(self):
        """Test cache expiration."""
        # Set a value with short TTL
        self.cache.set('test_key', 'test_value', ttl=1)

        # Should return the value immediately
        assert self.cache.get('test_key') == 'test_value'

        # Wait for expiration
        time.sleep(1.1)

        # Should return None after expiration
        assert self.cache.get('test_key') is None

    def test_cache_memory_limit(self):
        """Test memory cache size limits."""
        cache = CacheManager(max_memory_items=3)

        # Add items up to the limit
        for i in range(3):
            cache.set(f'key_{i}', f'value_{i}')

        assert len(cache._memory_cache) == 3

        # Add one more item
        cache.set('key_3', 'value_3')

        # Should still be at the limit (oldest evicted)
        assert len(cache._memory_cache) == 3
        assert 'key_0' not in cache._memory_cache  # Oldest should be evicted
        assert cache.get('key_3') == 'value_3'  # Newest should be present

    def test_cache_persistence(self):
        """Test disk persistence of cache."""
        # Set a value
        self.cache.set('persistent_key', 'persistent_value')

        # Create new cache manager with same directory
        cache2 = CacheManager(cache_dir=self.temp_dir)

        # Should be able to retrieve the persisted value
        result = cache2.get('persistent_key')
        assert result == 'persistent_value'

    def test_cache_clear(self):
        """Test cache clearing."""
        # Add some items
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')

        assert self.cache.get('key1') == 'value1'
        assert self.cache.get('key2') == 'value2'

        # Clear cache
        self.cache.clear()

        assert self.cache.get('key1') is None
        assert self.cache.get('key2') is None
        assert len(self.cache._memory_cache) == 0

    def test_cache_stats(self):
        """Test cache statistics."""
        stats = self.cache.get_stats()

        assert 'memory_items' in stats
        assert 'max_memory_items' in stats
        assert 'cache_dir' in stats
        assert 'disk_files' in stats

    def test_cached_function_decorator(self):
        """Test cached_function decorator."""
        call_count = 0

        @cached_function(ttl=3600)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call with same argument should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not have increased

        # Third call with different argument
        result3 = expensive_function(3)
        assert result3 == 6
        assert call_count == 2  # Should have increased

    def test_global_cache_functions(self):
        """Test global cache management functions."""
        # Clear global cache
        clear_cache()

        # Get stats
        stats = get_cache_stats()
        assert isinstance(stats, dict)


class TestPerformanceMonitor:
    """Test cases for PerformanceMonitor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        if not PERFORMANCE_MONITOR_AVAILABLE:
            pytest.skip("PerformanceMonitor not available (psutil not installed)")

        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.monitor = PerformanceMonitor(log_file=self.temp_file.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)

    def test_performance_monitor_initialization(self):
        """Test PerformanceMonitor initialization."""
        assert self.monitor.log_file == Path(self.temp_file.name)
        assert isinstance(self.monitor.metrics, list)
        assert hasattr(self.monitor, '_process')

    def test_record_metrics(self):
        """Test recording performance metrics."""
        self.monitor.record_metrics(
            function_name='test_function',
            execution_time=1.5,
            memory_usage_mb=50.0,
            cpu_percent=25.0,
            metadata={'test': True}
        )

        assert len(self.monitor.metrics) == 1
        metric = self.monitor.metrics[0]

        assert metric.function_name == 'test_function'
        assert metric.execution_time == 1.5
        assert metric.memory_usage_mb == 50.0
        assert metric.cpu_percent == 25.0
        assert metric.metadata == {'test': True}

    def test_get_stats_all_functions(self):
        """Test getting statistics for all functions."""
        # Record some metrics
        self.monitor.record_metrics('func1', 1.0, 10.0, 20.0)
        self.monitor.record_metrics('func1', 2.0, 15.0, 25.0)
        self.monitor.record_metrics('func2', 3.0, 20.0, 30.0)

        stats = self.monitor.get_stats()

        assert stats['total_calls'] == 3
        assert stats['execution_time']['min'] == 1.0
        assert stats['execution_time']['max'] == 3.0
        assert abs(stats['execution_time']['avg'] - 2.0) < 0.01
        assert stats['execution_time']['total'] == 6.0

    def test_get_stats_specific_function(self):
        """Test getting statistics for a specific function."""
        # Record metrics for different functions
        self.monitor.record_metrics('func1', 1.0, 10.0, 20.0)
        self.monitor.record_metrics('func1', 2.0, 15.0, 25.0)
        self.monitor.record_metrics('func2', 3.0, 20.0, 30.0)

        stats = self.monitor.get_stats('func1')

        assert stats['total_calls'] == 2
        assert stats['execution_time']['min'] == 1.0
        assert stats['execution_time']['max'] == 2.0

    def test_clear_metrics(self):
        """Test clearing performance metrics."""
        self.monitor.record_metrics('test_func', 1.0, 10.0, 20.0)
        assert len(self.monitor.metrics) == 1

        self.monitor.clear_metrics()
        assert len(self.monitor.metrics) == 0

    def test_export_metrics(self):
        """Test exporting metrics to file."""
        self.monitor.record_metrics('test_func', 1.0, 10.0, 20.0)

        export_file = tempfile.NamedTemporaryFile(delete=False)
        export_file.close()

        try:
            self.monitor.export_metrics(export_file.name)

            # Check that file was created and contains data
            with open(export_file.name) as f:
                data = json.load(f)

            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['function_name'] == 'test_func'

        finally:
            os.unlink(export_file.name)

    def test_monitor_performance_decorator(self):
        """Test monitor_performance decorator."""
        call_count = 0

        @monitor_performance()
        def test_function(x):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Small delay
            return x * 2

        # Clear any existing metrics
        clear_performance_metrics()

        # Call the function
        result = test_function(5)

        assert result == 10
        assert call_count == 1

        # Check that metrics were recorded in global monitor
        stats = get_performance_stats('test_function')
        assert stats['total_calls'] == 1
        assert stats['execution_time']['avg'] > 0

    def test_performance_context_manager(self):
        """Test performance_context context manager."""
        # Clear any existing metrics
        clear_performance_metrics()

        with performance_context('test_context'):
            time.sleep(0.01)

        # Check that metrics were recorded in global monitor
        stats = get_performance_stats('test_context')
        assert stats['total_calls'] == 1
        assert stats['execution_time']['avg'] > 0

    def test_global_performance_functions(self):
        """Test global performance monitoring functions."""
        # Clear metrics
        clear_performance_metrics()

        # Record a metric using the global monitor
        from codomyrmex.performance.performance_monitor import _performance_monitor
        _performance_monitor.record_metrics('global_test', 1.0, 10.0, 20.0)

        # Get stats via global function
        stats = get_performance_stats('global_test')
        assert stats['total_calls'] == 1
        assert stats['execution_time']['avg'] == 1.0


class TestIntegration:
    """Integration tests for performance module components."""

    def test_lazy_loading_with_caching(self):
        """Test lazy loading combined with caching."""
        # Create a lazy loader for json
        json_loader = lazy_import('json')

        @cached_function(ttl=3600)
        def cached_json_operation(data):
            # Access the lazy-loaded module
            return json_loader.dumps(data, indent=2)

        # First call should load json and cache result
        result1 = cached_json_operation({'test': 'data'})
        assert '"test": "data"' in result1

        # Second call should use cache
        result2 = cached_json_operation({'test': 'data'})
        assert result1 == result2

    @pytest.mark.skipif(not PERFORMANCE_MONITOR_AVAILABLE, reason="PerformanceMonitor not available")
    def test_performance_monitoring_with_caching(self):
        """Test performance monitoring combined with caching."""
        @monitor_performance()
        @cached_function(ttl=3600)
        def monitored_cached_function(x):
            time.sleep(0.01)  # Simulate work
            return x ** 2

        # First call - should do work and cache
        result1 = monitored_cached_function(5)
        assert result1 == 25

        # Second call - should use cache (faster)
        result2 = monitored_cached_function(5)
        assert result2 == 25

        # Check performance metrics
        stats = get_performance_stats('monitored_cached_function')
        assert stats['total_calls'] == 2

        # The second call should be faster due to caching
        # (This is a basic check - in practice you'd want more sophisticated timing)


if __name__ == '__main__':
    pytest.main([__file__])
