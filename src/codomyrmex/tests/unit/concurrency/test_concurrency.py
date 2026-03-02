"""Zero-Mock tests for concurrency module.

RedisLock tests use fakeredis for zero-mock, authentic behavior without a real Redis server.
"""

import asyncio
import threading
import time
import pytest
import fakeredis

from codomyrmex.concurrency import (
    LocalLock,
    LocalSemaphore,
    LockManager,
    ReadWriteLock,
    RedisLock,
    AsyncLocalSemaphore,
    AsyncWorkerPool
)

def test_local_lock_lifecycle(tmp_path):
    """Test the basic lifecycle of a LocalLock."""
    lock_dir = str(tmp_path / "locks")
    lock = LocalLock("test-lock", lock_dir=lock_dir)

    assert lock.acquire(timeout=1) is True
    assert lock.is_held is True

    def try_acquire(results):
        inner_lock = LocalLock("test-lock", lock_dir=lock_dir)
        results['acquired'] = inner_lock.acquire(timeout=0.2)
        if results['acquired']:
            inner_lock.release()

    results = {'acquired': None}
    t = threading.Thread(target=try_acquire, args=(results,))
    t.start()
    t.join()

    assert results['acquired'] is False

    lock.release()
    assert lock.is_held is False

def test_local_lock_reentry(tmp_path):
    """Test that LocalLock supports re-entry (recursion)."""
    lock_dir = str(tmp_path / "locks")
    lock = LocalLock("reentry-lock", lock_dir=lock_dir)
    
    assert lock.acquire(timeout=1) is True
    assert lock.acquire(timeout=1) is True  # Second acquisition
    
    lock.release()
    assert lock.is_held is True  # Still held due to nesting
    
    lock.release()
    assert lock.is_held is False

def test_local_semaphore():
    """Test the basic lifecycle of a LocalSemaphore."""
    sem = LocalSemaphore(value=2)

    assert sem.acquire(timeout=0.1) is True
    assert sem.acquire(timeout=0.1) is True
    assert sem.acquire(timeout=0.1) is False

    sem.release()
    assert sem.acquire(timeout=0.1) is True

def test_redis_lock_fakeredis():
    """Test RedisLock with fakeredis for zero-mock behavior."""
    client = fakeredis.FakeRedis()

    lock1 = RedisLock("test-redis-lock", client, ttl=10)
    lock2 = RedisLock("test-redis-lock", client, ttl=10)
    
    assert lock1.acquire(timeout=1) is True
    assert lock1.is_held is True
    assert lock2.acquire(timeout=0.1) is False
    
    assert lock1.is_locked_externally() is True
    
    assert lock1.extend(20) is True
    
    lock1.release()
    assert lock1.is_held is False
    assert lock1.is_locked_externally() is False
    
    assert lock2.acquire(timeout=1) is True
    assert lock2.is_held is True
    lock2.release()

def test_lock_manager(tmp_path):
    """Test LockManager multi-lock acquisition."""
    lock_dir = str(tmp_path / "locks")
    manager = LockManager()
    l1 = LocalLock("l1", lock_dir=lock_dir)
    l2 = LocalLock("l2", lock_dir=lock_dir)

    manager.register_lock("l1", l1)
    manager.register_lock("l2", l2)

    assert manager.acquire_all(["l1", "l2"], timeout=1) is True
    assert l1.is_held is True
    assert l2.is_held is True

    # Attempting to acquire again should fail (since they are already held by this thread, 
    # but acquire_all treats them as separate requests)
    # Actually, LocalLock is re-entrant, so acquire_all(["l1"]) would succeed.
    
    manager.release_all(["l1", "l2"])
    assert l1.is_held is False
    assert l2.is_held is False

def test_rw_lock_priorities():
    """Test ReadWriteLock reader/writer priorities."""
    rw = ReadWriteLock()
    results = []
    
    # Acquire a read lock
    rw.acquire_read()
    
    def try_write():
        # This should block until read is released
        if rw.acquire_write(timeout=2.0):
            results.append("writer")
            rw.release_write()

    def try_read():
        # This should block if a writer is waiting (priority to writers)
        if rw.acquire_read(timeout=2.0):
            results.append("reader")
            rw.release_read()

    tw = threading.Thread(target=try_write)
    tr = threading.Thread(target=try_read)
    
    tw.start()
    time.sleep(0.1) # Ensure writer starts waiting
    tr.start()
    
    time.sleep(0.1)
    rw.release_read() # Release initial read
    
    tw.join()
    tr.join()
    
    # Writer should have priority over the second reader
    assert results == ["writer", "reader"]

def test_lock_manager_stats(tmp_path):
    """Test LockManager.stats property."""
    lock_dir = str(tmp_path / "stats_locks")
    manager = LockManager()
    l1 = LocalLock("stats_l1", lock_dir=lock_dir)
    l2 = LocalLock("stats_l2", lock_dir=lock_dir)

    manager.register_lock("stats_l1", l1)
    manager.register_lock("stats_l2", l2)

    stats = manager.stats
    assert stats.total_locks == 2
    assert stats.total_acquisitions == 0

    manager.acquire_all(["stats_l1", "stats_l2"])
    stats = manager.stats
    assert stats.total_acquisitions == 2
    assert stats.active_locks == 2

    manager.release_all(["stats_l1", "stats_l2"])
    stats = manager.stats
    assert stats.total_releases == 2
    assert stats.active_locks == 0

@pytest.mark.asyncio
async def test_async_worker_pool():
    """Test AsyncWorkerPool functionality."""
    async def task(val):
        await asyncio.sleep(0.01)
        return val * 2

    async with AsyncWorkerPool(max_workers=2) as pool:
        results = await pool.map(task, [1, 2, 3, 4, 5])
        assert len(results) == 5
        assert all(r.success for r in results)
        assert [r.result for r in results] == [2, 4, 6, 8, 10]
        
        stats = pool.stats
        assert stats.completed == 5
        assert stats.submitted == 5

@pytest.mark.asyncio
async def test_async_semaphore_bridge():
    """Test AsyncLocalSemaphore sync/async bridging."""
    sem = AsyncLocalSemaphore(value=1)
    
    # Async acquire
    assert await sem.acquire_async() is True
    
    # Sync acquire (should fail/timeout since already held)
    # Using a small timeout to avoid blocking too long
    assert sem.acquire(timeout=0.1) is False
    
    sem.release()
    
    # Sync acquire (should succeed)
    assert sem.acquire(timeout=1.0) is True
    sem.release()
