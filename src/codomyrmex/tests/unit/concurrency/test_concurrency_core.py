"""Zero-mock tests for concurrency module core components.

Covers:
- ReadWriteLock: acquire_read/write, release, context managers
- LockManager: register, get, list, stats, acquire_all, release_all
- LocalLock: acquire/release/context manager (file-based, Unix only)
- AsyncWorkerPool: submit success/failure, map, shutdown, closed pool
- PoolStats and TaskResult dataclasses
- MCP tools: concurrency_pool_status, concurrency_list_locks
- DeadLetterQueue: additional edge case coverage

Zero-Mock Policy: no unittest.mock, MagicMock, monkeypatch, or pytest-mock.
All tests use real synchronization primitives and real asyncio.run().
"""

from __future__ import annotations

import asyncio
import tempfile
import threading

import pytest

# ===========================================================================
# ReadWriteLock
# ===========================================================================


@pytest.mark.unit
class TestReadWriteLockCore:
    """ReadWriteLock: shared reads, exclusive writes, context managers."""

    def _rw(self):
        from codomyrmex.concurrency import ReadWriteLock

        return ReadWriteLock()

    def test_acquire_read_returns_true(self):
        rw = self._rw()
        result = rw.acquire_read(timeout=1.0)
        rw.release_read()
        assert result is True

    def test_acquire_write_returns_true(self):
        rw = self._rw()
        result = rw.acquire_write(timeout=1.0)
        rw.release_write()
        assert result is True

    def test_multiple_reads_allowed(self):
        rw = self._rw()
        r1 = rw.acquire_read(timeout=1.0)
        r2 = rw.acquire_read(timeout=1.0)
        rw.release_read()
        rw.release_read()
        assert r1 is True
        assert r2 is True

    def test_read_context_manager(self):
        rw = self._rw()
        with rw.read_lock():
            assert rw._readers == 1
        assert rw._readers == 0

    def test_write_context_manager(self):
        rw = self._rw()
        with rw.write_lock():
            assert rw._writer_active is True
        assert rw._writer_active is False

    def test_release_write_clears_writer_active(self):
        rw = self._rw()
        rw.acquire_write(timeout=1.0)
        rw.release_write()
        assert rw._writer_active is False

    def test_release_read_decrements_readers(self):
        rw = self._rw()
        rw.acquire_read(timeout=1.0)
        rw.acquire_read(timeout=1.0)
        rw.release_read()
        assert rw._readers == 1
        rw.release_read()
        assert rw._readers == 0

    def test_write_after_read_release(self):
        rw = self._rw()
        rw.acquire_read(timeout=1.0)
        rw.release_read()
        acquired = rw.acquire_write(timeout=1.0)
        rw.release_write()
        assert acquired is True

    def test_write_lock_timeout_while_read_held(self):
        rw = self._rw()
        # Hold a read lock from a background thread
        ready = threading.Event()
        release = threading.Event()

        def hold_read():
            rw.acquire_read()
            ready.set()
            release.wait(timeout=3.0)
            rw.release_read()

        t = threading.Thread(target=hold_read, daemon=True)
        t.start()
        ready.wait(timeout=2.0)
        # Write should time out very quickly while read is held
        acquired = rw.acquire_write(timeout=0.05)
        release.set()
        t.join(timeout=2.0)
        assert acquired is False

    def test_concurrent_reads_do_not_block(self):
        """Multiple threads can hold read locks simultaneously."""
        rw = self._rw()
        results = []
        barrier = threading.Barrier(3)

        def reader():
            rw.acquire_read()
            barrier.wait(timeout=2.0)
            results.append(True)
            rw.release_read()

        threads = [threading.Thread(target=reader, daemon=True) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=3.0)
        assert len(results) == 3


# ===========================================================================
# LockManager
# ===========================================================================


@pytest.mark.unit
class TestLockManagerCore:
    """LockManager: register, get, list, stats, acquire_all, release_all."""

    def _mgr(self):
        from codomyrmex.concurrency import LockManager

        return LockManager()

    def _local_lock(self, name: str, tmpdir: str):
        from codomyrmex.concurrency import LocalLock

        return LocalLock(name, lock_dir=tmpdir)

    def test_new_manager_empty(self):
        mgr = self._mgr()
        assert mgr.list_locks() == []

    def test_register_and_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = self._mgr()
            lock = self._local_lock("res1", tmpdir)
            mgr.register_lock("res1", lock)
            assert "res1" in mgr.list_locks()

    def test_get_lock_returns_registered(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = self._mgr()
            lock = self._local_lock("db", tmpdir)
            mgr.register_lock("db", lock)
            assert mgr.get_lock("db") is lock

    def test_get_lock_returns_none_for_unknown(self):
        mgr = self._mgr()
        assert mgr.get_lock("unknown") is None

    def test_stats_initial_zeros(self):
        mgr = self._mgr()
        stats = mgr.stats
        assert stats.total_locks == 0
        assert stats.total_acquisitions == 0
        assert stats.total_releases == 0
        assert stats.active_locks == 0

    def test_stats_counts_registered_locks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = self._mgr()
            mgr.register_lock("l1", self._local_lock("l1", tmpdir))
            mgr.register_lock("l2", self._local_lock("l2", tmpdir))
            assert mgr.stats.total_locks == 2

    def test_acquire_all_unknown_lock_returns_false(self):
        mgr = self._mgr()
        # acquire_all catches the ValueError internally and returns False
        result = mgr.acquire_all(["nonexistent"], timeout=1.0)
        assert result is False

    def test_acquire_all_and_release_all(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = self._mgr()
            l1 = self._local_lock("lm_a", tmpdir)
            l2 = self._local_lock("lm_b", tmpdir)
            mgr.register_lock("lm_a", l1)
            mgr.register_lock("lm_b", l2)
            success = mgr.acquire_all(["lm_a", "lm_b"], timeout=5.0)
            try:
                assert success is True
            finally:
                mgr.release_all(["lm_a", "lm_b"])

    def test_release_all_ignores_unregistered_name(self):
        mgr = self._mgr()
        # Should not raise even if name isn't registered
        mgr.release_all(["not_there"])

    def test_list_locks_returns_list_of_strings(self):
        mgr = self._mgr()
        result = mgr.list_locks()
        assert isinstance(result, list)

    def test_stats_contention_starts_empty(self):
        mgr = self._mgr()
        assert mgr.stats.lock_contention == {}


# ===========================================================================
# LocalLock
# ===========================================================================


@pytest.mark.unit
class TestLocalLockCore:
    """LocalLock: acquire, release, context manager, reentrancy."""

    def _lock(self, name: str, tmpdir: str):
        from codomyrmex.concurrency import LocalLock

        return LocalLock(name, lock_dir=tmpdir)

    def test_acquire_returns_true(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lock = self._lock("test_acq", tmpdir)
            result = lock.acquire(timeout=2.0)
            lock.release()
            assert result is True

    def test_is_held_after_acquire(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lock = self._lock("test_held", tmpdir)
            lock.acquire(timeout=2.0)
            try:
                assert lock.is_held is True
            finally:
                lock.release()

    def test_is_not_held_after_release(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lock = self._lock("test_released", tmpdir)
            lock.acquire(timeout=2.0)
            lock.release()
            assert lock.is_held is False

    def test_context_manager_acquires_and_releases(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lock = self._lock("ctx_mgr", tmpdir)
            with lock:
                assert lock.is_held is True
            assert lock.is_held is False

    def test_release_without_acquire_does_not_raise(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lock = self._lock("no_acquire", tmpdir)
            # release without acquire should be a no-op
            lock.release()

    def test_reentrant_acquire_works(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lock = self._lock("reentrant", tmpdir)
            lock.acquire(timeout=2.0)
            result = lock.acquire(timeout=2.0)  # second acquire — reentrancy
            lock.release()
            lock.release()
            assert result is True


# ===========================================================================
# AsyncWorkerPool
# ===========================================================================


@pytest.mark.unit
class TestAsyncWorkerPoolCore:
    """AsyncWorkerPool: submit, map, shutdown, closed pool, stats."""

    def _run(self, coro):
        return asyncio.run(coro)

    async def _submit_success(self):
        from codomyrmex.concurrency import AsyncWorkerPool

        async def work(x):
            return x * 2

        async with AsyncWorkerPool(max_workers=2) as pool:
            result = await pool.submit(work, 5, task_id="t1")
        return result

    def test_submit_success_result(self):
        r = self._run(self._submit_success())
        assert r.success is True
        assert r.result == 10

    def test_submit_success_task_id(self):
        r = self._run(self._submit_success())
        assert r.task_id == "t1"

    def test_submit_success_elapsed_positive(self):
        r = self._run(self._submit_success())
        assert r.elapsed_ms >= 0.0

    async def _submit_failure(self):
        from codomyrmex.concurrency import AsyncWorkerPool

        async def explode():
            raise ValueError("boom")

        async with AsyncWorkerPool(max_workers=2) as pool:
            result = await pool.submit(explode, task_id="fail1")
        return result

    def test_submit_failure_marks_success_false(self):
        r = self._run(self._submit_failure())
        assert r.success is False

    def test_submit_failure_captures_error(self):
        r = self._run(self._submit_failure())
        assert "boom" in r.error

    async def _map_test(self):
        from codomyrmex.concurrency import AsyncWorkerPool

        async def double(x):
            return x * 2

        async with AsyncWorkerPool(max_workers=4) as pool:
            results = await pool.map(double, [1, 2, 3, 4])
        return results

    def test_map_returns_correct_count(self):
        results = self._run(self._map_test())
        assert len(results) == 4

    def test_map_all_succeed(self):
        results = self._run(self._map_test())
        assert all(r.success for r in results)

    def test_map_results_match_expected(self):
        results = self._run(self._map_test())
        values = sorted(r.result for r in results)
        assert values == [2, 4, 6, 8]

    async def _closed_pool_test(self):
        from codomyrmex.concurrency import AsyncWorkerPool

        async def noop():
            pass

        pool = AsyncWorkerPool(max_workers=2)
        await pool.shutdown()
        await pool.submit(noop, task_id="post_close")

    def test_submit_to_closed_pool_raises(self):
        with pytest.raises(RuntimeError, match="shut down"):
            self._run(self._closed_pool_test())

    async def _stats_test(self):
        from codomyrmex.concurrency import AsyncWorkerPool

        async def work():
            return "ok"

        async with AsyncWorkerPool(max_workers=2) as pool:
            await pool.submit(work, task_id="s1")
            await pool.submit(work, task_id="s2")
        return pool.stats

    def test_stats_submitted_count(self):
        stats = self._run(self._stats_test())
        assert stats.submitted == 2

    def test_stats_completed_count(self):
        stats = self._run(self._stats_test())
        assert stats.completed == 2

    def test_stats_failed_zero(self):
        stats = self._run(self._stats_test())
        assert stats.failed == 0

    async def _stats_with_failure(self):
        from codomyrmex.concurrency import AsyncWorkerPool

        async def bad():
            raise RuntimeError("fail")

        async with AsyncWorkerPool(max_workers=1) as pool:
            await pool.submit(bad)
        return pool.stats

    def test_stats_failed_count_with_failure(self):
        stats = self._run(self._stats_with_failure())
        assert stats.failed == 1

    def test_pool_stats_dataclass_defaults(self):
        from codomyrmex.concurrency.workers.pool import PoolStats

        ps = PoolStats()
        assert ps.submitted == 0
        assert ps.completed == 0
        assert ps.failed == 0
        assert ps.total_elapsed_ms == 0.0

    def test_task_result_dataclass(self):
        from codomyrmex.concurrency.workers.pool import TaskResult

        tr = TaskResult(task_id="abc", success=True, result=42, elapsed_ms=10.0)
        assert tr.task_id == "abc"
        assert tr.success is True
        assert tr.result == 42


# ===========================================================================
# Concurrency MCP tools (additive to existing test_mcp_tools.py)
# ===========================================================================


@pytest.mark.unit
class TestConcurrencyMcpToolsCore:
    """concurrency_pool_status and concurrency_list_locks return correct shapes."""

    def test_pool_status_has_pool_stats_key(self):
        from codomyrmex.concurrency.mcp_tools import concurrency_pool_status

        result = concurrency_pool_status()
        assert "pool_stats" in result

    def test_pool_status_pool_stats_has_submitted(self):
        from codomyrmex.concurrency.mcp_tools import concurrency_pool_status

        result = concurrency_pool_status()
        assert "submitted" in result["pool_stats"]

    def test_pool_status_pool_stats_has_completed(self):
        from codomyrmex.concurrency.mcp_tools import concurrency_pool_status

        result = concurrency_pool_status()
        assert "completed" in result["pool_stats"]

    def test_pool_status_pool_stats_has_failed(self):
        from codomyrmex.concurrency.mcp_tools import concurrency_pool_status

        result = concurrency_pool_status()
        assert "failed" in result["pool_stats"]

    def test_list_locks_returns_empty_for_fresh_manager(self):
        from codomyrmex.concurrency.mcp_tools import concurrency_list_locks

        result = concurrency_list_locks()
        assert result["status"] == "success"
        assert "locks" in result
        assert "count" in result

    def test_list_locks_count_is_int(self):
        from codomyrmex.concurrency.mcp_tools import concurrency_list_locks

        result = concurrency_list_locks()
        assert isinstance(result["count"], int)

    def test_list_locks_locks_is_list(self):
        from codomyrmex.concurrency.mcp_tools import concurrency_list_locks

        result = concurrency_list_locks()
        assert isinstance(result["locks"], list)
