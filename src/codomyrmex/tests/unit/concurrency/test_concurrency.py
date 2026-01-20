"""Unit tests for the concurrency module."""

import pytest
import time
import threading
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
