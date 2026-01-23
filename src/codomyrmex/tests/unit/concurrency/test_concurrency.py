"""Unit tests for the concurrency module."""

import pytest
import time
import threading
import asyncio
from unittest.mock import MagicMock
from codomyrmex.concurrency import LocalLock, LocalSemaphore, RedisLock, LockManager, ReadWriteLock

def test_local_lock_lifecycle(tmp_path):
    """Test the basic lifecycle of a LocalLock."""
    lock_dir = str(tmp_path / "locks")
    lock = LocalLock("test-lock", lock_dir=lock_dir)
    
    # Assert acquisition works
    assert lock.acquire(timeout=1) is True
    assert lock.is_held is True
    
    # Assert re-acquisition from same instance fails (fcntl behavior)
    # Actually fcntl locks are per-process, so same process can re-lock? 
    # Let's test with a thread.
    
    def try_acquire(results):
        inner_lock = LocalLock("test-lock", lock_dir=lock_dir)
        results['acquired'] = inner_lock.acquire(timeout=0.1)
        if results['acquired']:
            inner_lock.release()

    results = {'acquired': None}
    t = threading.Thread(target=try_acquire, args=(results,))
    t.start()
    t.join()
    
    assert results['acquired'] is False
    
    lock.release()
    assert lock.is_held is False

def test_local_semaphore():
    """Test the basic lifecycle of a LocalSemaphore."""
    sem = LocalSemaphore(value=2)
    
    assert sem.acquire(timeout=0.1) is True
    assert sem.acquire(timeout=0.1) is True
    assert sem.acquire(timeout=0.1) is False # Max capacity reached
    
    sem.release()
    assert sem.acquire(timeout=0.1) is True

def test_redis_lock_mock():
    """Test RedisLock with a mocked redis client."""
    mock_redis = MagicMock()
    # Mock successful acquisition
    mock_redis.set.return_value = True
    
    lock = RedisLock("test-redis-lock", mock_redis)
    assert lock.acquire(timeout=1) is True
    assert lock.is_held is True
    
    mock_redis.set.assert_called_once()
    
    # Mock successful release
    mock_redis.eval.return_value = 1
    lock.release()
    assert lock.is_held is False
    mock_redis.eval.assert_called_once()

def test_lock_manager(tmp_path):
    """Test LockManager multi-lock acquisition."""
    lock_dir = str(tmp_path / "locks")
    manager = LockManager()
    l1 = LocalLock("l1", lock_dir=lock_dir)
    l2 = LocalLock("l2", lock_dir=lock_dir)
    
    manager.register_lock("l1", l1)
    manager.register_lock("l2", l2)
    
    assert manager.acquire_all(["l1", "l2"]) is True
    assert l1.is_held is True
    assert l2.is_held is True
    
    manager.release_all(["l1", "l2"])
    assert l1.is_held is False
    assert l2.is_held is False

def test_rw_lock():
    """Test ReadWriteLock basic functionality."""
    rw = ReadWriteLock()
    
    # Test read shared
    rw.acquire_read()
    rw.acquire_read()
    rw.release_read()
    rw.release_read()
    
    # Test write exclusive
    rw.acquire_write()
    # If we tried to acquire_read here in another thread, it would block
    rw.release_write()

def test_lock_manager_stats(tmp_path):
    """Test LockManager.stats property for Unified Streamline compliance."""
    from codomyrmex.concurrency.lock_manager import LockStats
    
    lock_dir = str(tmp_path / "stats_locks")
    manager = LockManager()
    l1 = LocalLock("stats_l1", lock_dir=lock_dir)
    l2 = LocalLock("stats_l2", lock_dir=lock_dir)
    
    manager.register_lock("stats_l1", l1)
    manager.register_lock("stats_l2", l2)
    
    # Get initial stats
    stats = manager.stats
    assert isinstance(stats, LockStats)
    assert stats.total_locks == 2
    assert stats.total_acquisitions == 0
    assert stats.total_releases == 0
    
    # Acquire and check counters
    manager.acquire_all(["stats_l1", "stats_l2"])
    stats = manager.stats
    assert stats.total_acquisitions == 2
    
    # Release and check counters
    manager.release_all(["stats_l1", "stats_l2"])
    stats = manager.stats
    assert stats.total_releases == 2


# ==================== ASYNC TESTS ====================

@pytest.mark.asyncio
class TestAsyncSemaphore:
    """Async tests for AsyncLocalSemaphore."""

    async def test_async_semaphore_acquire_release(self):
        """Test basic async semaphore acquire and release."""
        from codomyrmex.concurrency.semaphore import AsyncLocalSemaphore

        sem = AsyncLocalSemaphore(value=2)

        # Acquire twice should work
        await sem.acquire_async()
        await sem.acquire_async()

        # Release
        sem.release()
        sem.release()

    async def test_async_semaphore_blocking(self):
        """Test async semaphore blocks when exhausted."""
        from codomyrmex.concurrency.semaphore import AsyncLocalSemaphore

        sem = AsyncLocalSemaphore(value=1)

        # Acquire the single permit
        await sem.acquire_async()

        # Try to acquire with timeout
        acquired = False
        try:
            await asyncio.wait_for(sem.acquire_async(), timeout=0.1)
            acquired = True
        except asyncio.TimeoutError:
            pass

        assert acquired is False

        # Release and now acquire should work
        sem.release()
        await asyncio.wait_for(sem.acquire_async(), timeout=0.5)

    async def test_async_semaphore_concurrent_access(self):
        """Test concurrent async semaphore access."""
        from codomyrmex.concurrency.semaphore import AsyncLocalSemaphore

        sem = AsyncLocalSemaphore(value=3)
        counter = 0
        max_concurrent = 0

        async def worker(worker_id):
            nonlocal counter, max_concurrent
            await sem.acquire_async()
            counter += 1
            max_concurrent = max(max_concurrent, counter)
            await asyncio.sleep(0.05)
            counter -= 1
            sem.release()

        # Run 10 workers concurrently
        await asyncio.gather(*[worker(i) for i in range(10)])

        # Max concurrent should never exceed semaphore value
        assert max_concurrent <= 3

    async def test_async_semaphore_sync_acquire_raises(self):
        """Test that sync acquire raises NotImplementedError."""
        from codomyrmex.concurrency.semaphore import AsyncLocalSemaphore

        sem = AsyncLocalSemaphore(value=1)

        with pytest.raises(NotImplementedError):
            sem.acquire()


@pytest.mark.asyncio
class TestAsyncLockPatterns:
    """Async tests for common locking patterns."""

    async def test_async_resource_access(self):
        """Test async resource access pattern."""
        from codomyrmex.concurrency.semaphore import AsyncLocalSemaphore

        # Simulate a resource pool with limited connections
        connection_pool = AsyncLocalSemaphore(value=2)
        results = []

        async def use_connection(task_id):
            await connection_pool.acquire_async()
            try:
                results.append(f"start_{task_id}")
                await asyncio.sleep(0.02)
                results.append(f"end_{task_id}")
            finally:
                connection_pool.release()

        # Run 5 tasks with only 2 "connections"
        await asyncio.gather(*[use_connection(i) for i in range(5)])

        # All tasks should complete
        assert len([r for r in results if r.startswith("start")]) == 5
        assert len([r for r in results if r.startswith("end")]) == 5

    async def test_async_producer_consumer(self):
        """Test async producer-consumer pattern."""
        from codomyrmex.concurrency.semaphore import AsyncLocalSemaphore

        buffer_size = 3
        available_slots = AsyncLocalSemaphore(buffer_size)
        available_items = AsyncLocalSemaphore(0)

        buffer = []
        produced = 0
        consumed = 0

        async def producer(count):
            nonlocal produced
            for i in range(count):
                await available_slots.acquire_async()
                buffer.append(i)
                produced += 1
                available_items.release()

        async def consumer(count):
            nonlocal consumed
            for _ in range(count):
                await available_items.acquire_async()
                buffer.pop(0)
                consumed += 1
                available_slots.release()

        # Producer produces 5 items, consumer consumes 5 items
        await asyncio.gather(producer(5), consumer(5))

        assert produced == 5
        assert consumed == 5
        assert len(buffer) == 0

    async def test_async_rate_limiter(self):
        """Test async rate limiting pattern."""
        from codomyrmex.concurrency.semaphore import AsyncLocalSemaphore
        import time

        # Allow 3 operations per "window"
        rate_limiter = AsyncLocalSemaphore(value=3)

        async def rate_limited_operation(op_id):
            await rate_limiter.acquire_async()
            return op_id

        start_time = time.time()

        # Run 6 operations
        results = []
        for batch in [[0, 1, 2], [3, 4, 5]]:
            batch_results = await asyncio.gather(
                *[rate_limited_operation(i) for i in batch]
            )
            results.extend(batch_results)
            # Release for next batch
            for _ in batch:
                rate_limiter.release()

        assert len(results) == 6
