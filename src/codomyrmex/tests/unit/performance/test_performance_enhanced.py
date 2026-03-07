"""Enhanced zero-mock unit tests for the performance module and resource manager."""

import shutil
import tempfile
import time

from codomyrmex.logistics.orchestration.project.resource_manager import (
    Resource,
    ResourceManager,
    ResourceStatus,
    ResourceType,
)
from codomyrmex.performance.benchmarking.benchmark_runner import BenchmarkRunner
from codomyrmex.performance.caching.cache_manager import CacheManager
from codomyrmex.performance.optimization.lazy_loader import LazyLoader


class TestResourceManagerEnhanced:
    """Enhanced tests for ResourceManager lifecycle."""

    def test_resource_manager_lifecycle(self):
        """Test the full lifecycle of resource allocation and release."""
        mgr = ResourceManager()

        # Initial state (default resources)
        compute = mgr.get_resource("sys-compute")
        assert compute is not None
        assert compute.status == ResourceStatus.AVAILABLE
        assert compute.allocated == 0.0

        # Allocate
        alloc = mgr.allocate("sys-compute", "test-requester", amount=50.0)
        assert alloc is not None
        assert alloc.amount == 50.0
        assert compute.allocated == 50.0
        assert compute.status == ResourceStatus.ALLOCATED

        # Allocate more (fill capacity)
        alloc2 = mgr.allocate("sys-compute", "test-requester-2", amount=50.0)
        assert alloc2 is not None
        assert compute.allocated == 100.0
        assert compute.status == ResourceStatus.BUSY

        # Try to allocate over capacity
        alloc3 = mgr.allocate("sys-compute", "test-requester-3", amount=1.0)
        assert alloc3 is None

        # Release one
        success = mgr.release(alloc.allocation_id)
        assert success is True
        assert compute.allocated == 50.0
        assert compute.status == ResourceStatus.ALLOCATED

        # Release other
        success2 = mgr.release(alloc2.allocation_id)
        assert success2 is True
        assert compute.allocated == 0.0
        assert compute.status == ResourceStatus.AVAILABLE

    def test_custom_resource_addition(self):
        """Test adding and managing a custom resource."""
        mgr = ResourceManager()
        custom_res = Resource(
            id="gpu-0",
            name="NVIDIA V100",
            type=ResourceType.CUSTOM,
            capacity=1.0,
            metadata={"memory": "16GB"},
        )
        mgr.add_resource(custom_res)

        assert mgr.get_resource("gpu-0") == custom_res

        alloc = mgr.allocate("gpu-0", "agent-1", amount=1.0)
        assert alloc is not None
        assert custom_res.status == ResourceStatus.BUSY


class TestCacheManagerEnhanced:
    """Enhanced tests for CacheManager eviction policies."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_lru_eviction_order(self):
        """Test that the LRU eviction policy correctly removes the least recently used item."""
        # Max 2 items in memory
        cache = CacheManager(cache_dir=self.temp_dir, max_memory_items=2)

        cache.set("a", 1)
        cache.set("b", 2)

        # Access "a" to make it most recently used
        cache.get("a")

        # Set "c", which should evict "b" (since "a" was accessed last)
        cache.set("c", 3)

        assert "a" in cache._memory_cache
        assert "c" in cache._memory_cache
        assert "b" not in cache._memory_cache

        # Verify persistence still has it though (disk cache is separate and doesn't have same limit in this implementation)
        # Actually CacheManager.set writes to disk too.
        # But _evict_oldest only removes from _memory_cache in my implementation.

    def test_get_updates_lru_order(self):
        """Test that get() updates the LRU order in memory."""
        cache = CacheManager(cache_dir=self.temp_dir, max_memory_items=2)

        cache.set("a", 1)
        cache.set("b", 2)

        # Current order: a, b (b is newest)
        # Access a
        cache.get("a")
        # Now order: b, a (a is newest)

        cache.set("c", 3)
        # Should evict b

        assert "b" not in cache._memory_cache
        assert "a" in cache._memory_cache
        assert "c" in cache._memory_cache


class TestLazyLoaderEnhanced:
    """Enhanced tests for LazyLoader initialization."""

    def test_lazy_initialization_deferred(self):
        """Test that module import is truly deferred until attribute access."""
        # Use a module that is definitely not imported yet in this test session
        # (or at least check it)
        import sys

        module_name = "calendar"
        if module_name in sys.modules:
            # If it's already there, we can't easily test deferral of the ACTUAL import
            # but we can test our wrapper's state
            pass

        loader = LazyLoader(module_name)
        assert loader._module is None

        # Access an attribute
        _ = loader.month_name

        assert loader._module is not None
        assert loader._module.__name__ == module_name


class TestBenchmarkTimingEnhanced:
    """Enhanced tests for benchmark timing accuracy."""

    def test_warmup_iterations(self):
        """Test that warm-up iterations are executed."""
        runner = BenchmarkRunner()

        count = 0

        def bench_fn():
            nonlocal count
            count += 1

        runner.add("test", bench_fn, iterations=5, warmup_iterations=2)
        runner.run()

        # Total calls should be iterations + warmup_iterations
        assert count == 7

    def test_timing_accuracy(self):
        """Test that timing is reasonably accurate for a sleep operation."""
        runner = BenchmarkRunner()

        def slow_fn():
            time.sleep(0.05)  # 50ms

        runner.add("sleep_50ms", slow_fn, iterations=3)
        suite = runner.run()

        result = suite.results[0]
        # Mean should be close to 50ms. Allow some overhead.
        assert 45 <= result.mean_ms <= 100
