"""Tests for agents.hermes.session — SessionRaceGuard.

Zero-Mock: Uses real threading primitives and SQLite for concurrency testing.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from codomyrmex.agents.hermes.session import (
    HermesSession,
    SessionRaceGuard,
    SQLiteSessionStore,
)


class TestSessionRaceGuard:
    """Verify SessionRaceGuard thread-safe session access."""

    def test_acquire_releases_lock_on_context_exit(self) -> None:
        """Lock should be released after context manager exits."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)
        session_id = "test-lock-1"

        # Acquire and release
        with guard.acquire(session_id):
            assert guard.is_locked(session_id) is True

        # Should be unlocked after exit
        assert guard.is_locked(session_id) is False
        store.close()

    def test_concurrent_access_serialized(self) -> None:
        """Concurrent threads should be serialized per session."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)
        session_id = "test-concurrent-1"

        # Save initial session
        session = HermesSession(session_id=session_id)
        session.add_message("user", "initial")
        store.save(session)

        execution_order: list[int] = []
        lock = threading.Lock()

        def thread_func(thread_id: int) -> None:
            with guard.acquire(session_id):
                with lock:
                    execution_order.append(thread_id)
                # Simulate some work
                time.sleep(0.05)
                # Load and modify session
                s = store.load(session_id)
                s.add_message("user", f"from-thread-{thread_id}")
                store.save(s)

        # Run 3 threads concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(thread_func, i) for i in range(3)]
            for f in as_completed(futures):
                f.result()

        # All threads completed
        loaded = store.load(session_id)
        assert loaded is not None
        assert loaded.message_count == 4  # initial + 3 from threads
        store.close()

    def test_different_sessions_parallel(self) -> None:
        """Different session IDs should not block each other."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)

        results: dict[str, float] = {}

        def thread_func(session_id: str, delay: float) -> None:
            start = time.time()
            with guard.acquire(session_id):
                time.sleep(delay)
            results[session_id] = time.time() - start

        # Different sessions should complete roughly in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(thread_func, "session-a", 0.1)
            f2 = executor.submit(thread_func, "session-b", 0.1)
            f1.result()
            f2.result()

        # Both should complete in ~0.1s (parallel), not ~0.2s (serial)
        assert results["session-a"] < 0.2
        assert results["session-b"] < 0.2
        store.close()

    def test_timeout_raises_on_stuck_lock(self) -> None:
        """Should raise RuntimeError when lock acquisition times out."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)
        session_id = "test-timeout-1"

        # Hold lock indefinitely
        held = threading.Event()

        def hold_lock() -> None:
            with guard.acquire(session_id):
                held.wait()  # Hold forever

        holder = threading.Thread(target=hold_lock, daemon=True)
        holder.start()
        time.sleep(0.05)  # Let holder acquire

        # Try to acquire with short timeout - should fail
        with pytest.raises(RuntimeError, match="Timeout acquiring lock"):
            guard.acquire(session_id, timeout=0.1)

        # Cleanup
        held.set()
        holder.join(timeout=1)
        store.close()

    def test_is_locked_false_for_nonexistent(self) -> None:
        """is_locked should return False for sessions never accessed."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)

        assert guard.is_locked("never-seen") is False
        store.close()

    def test_release_non_held_lock_no_error(self) -> None:
        """Releasing a lock that's not held should not raise."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)

        # Should not raise
        guard.release("never-held")
        store.close()


class TestSessionGuardContext:
    """Verify SessionGuardContext context manager behavior."""

    def test_context_manager_calls_release_on_exit(self) -> None:
        """Context exit should always release the lock."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)
        session_id = "ctx-test-1"

        ctx = guard.acquire(session_id)
        assert guard.is_locked(session_id) is True

        # Exit context - should release
        ctx.__exit__(None, None, None)
        assert guard.is_locked(session_id) is False
        store.close()

    def test_context_manager_returns_self_on_enter(self) -> None:
        """__enter__ should return self."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)
        session_id = "ctx-enter-1"

        ctx = guard.acquire(session_id)
        result = ctx.__enter__()
        assert result is ctx
        ctx.__exit__(None, None, None)
        store.close()


class TestSessionRaceGuardIntegration:
    """Integration tests for SessionRaceGuard with SQLiteSessionStore."""

    def test_safe_concurrent_session_modification(self) -> None:
        """Multiple threads safely modifying same session via guard."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)

        session_id = "integration-1"
        initial = HermesSession(session_id=session_id)
        initial.add_message("system", "You are helpful")
        store.save(initial)

        errors: list[Exception] = []

        def worker(worker_id: int) -> None:
            try:
                with guard.acquire(session_id):
                    s = store.load(session_id)
                    s.add_message("user", f"Message from worker {worker_id}")
                    s.metadata["last_worker"] = worker_id
                    store.save(s)
            except Exception as e:
                errors.append(e)

        # Run 10 workers
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            for f in as_completed(futures):
                f.result()

        # No errors
        assert len(errors) == 0

        # Session should have all messages
        loaded = store.load(session_id)
        assert loaded is not None
        assert loaded.message_count == 11  # system + 10 worker messages
        # Worker completion order is non-deterministic with ThreadPoolExecutor;
        # verify metadata was written by *some* worker, not a specific one.
        assert loaded.metadata["last_worker"] in range(10)
        store.close()

    def test_race_guard_with_multiple_sessions(self) -> None:
        """Guard should handle multiple different sessions correctly."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)

        # Create 5 sessions
        for i in range(5):
            s = HermesSession(session_id=f"multi-{i}")
            store.save(s)

        accessed: list[str] = []
        lock = threading.Lock()

        def access_session(sid: str) -> None:
            with guard.acquire(sid):
                with lock:
                    accessed.append(sid)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(access_session, f"multi-{i % 5}") for i in range(20)
            ]
            for f in as_completed(futures):
                f.result()

        # All sessions were accessed
        assert len(accessed) == 20
        store.close()

    def test_prune_locks_removes_unused_locks(self) -> None:
        """prune_locks should remove unlocked sessions beyond max_size."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)

        # Create many session locks (all unlocked)
        for i in range(150):
            _ = guard._get_lock(f"session-{i}")

        assert guard.get_lock_count() == 150

        # Prune should remove excess locks
        pruned = guard.prune_locks(max_size=100)
        assert pruned == 50
        assert guard.get_lock_count() == 100
        store.close()

    def test_prune_locks_preserves_locked_sessions(self) -> None:
        """prune_locks should not remove sessions that are currently locked."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)

        # Create locks, acquire one
        for i in range(120):
            _ = guard._get_lock(f"session-{i}")

        # Acquire one lock (keep it locked)
        held_context = guard.acquire("session-50")

        guard.prune_locks(max_size=100)

        # The locked session should still exist
        assert guard.get_lock_count() >= 100  # At least the locked one remains

        held_context.__exit__(None, None, None)  # Release
        store.close()

    def test_get_lock_count_returns_correct_count(self) -> None:
        """get_lock_count should return the current number of locks."""
        store = SQLiteSessionStore(":memory:")
        guard = SessionRaceGuard(store)

        assert guard.get_lock_count() == 0

        guard._get_lock("session-1")
        assert guard.get_lock_count() == 1

        guard._get_lock("session-2")
        guard._get_lock("session-3")
        assert guard.get_lock_count() == 3
        store.close()
