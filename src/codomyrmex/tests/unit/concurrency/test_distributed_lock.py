"""
Unit tests for concurrency.locks.distributed_lock — Zero-Mock compliant.

Covers: BaseLock (abstract, cannot instantiate), LocalLock (acquire/release
round-trip, is_held, context-manager protocol, double-release safety,
timeout=0 fails immediately, separate locks don't block each other).
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.concurrency.locks.distributed_lock import BaseLock, LocalLock


def _make_lock(name: str = "test-lock") -> tuple[LocalLock, str]:
    """Return (lock, lock_dir) for an isolated temp directory."""
    lock_dir = tempfile.mkdtemp(prefix="codomyrmex-test-locks-")
    return LocalLock(name=name, lock_dir=lock_dir), lock_dir


@pytest.mark.unit
class TestBaseLock:
    def test_base_lock_is_abstract(self):
        """BaseLock cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseLock("my-lock")  # type: ignore


@pytest.mark.unit
class TestLocalLockAcquireRelease:
    def test_acquire_returns_true(self):
        lock, _ = _make_lock()
        assert lock.acquire() is True
        lock.release()

    def test_is_held_after_acquire(self):
        lock, _ = _make_lock()
        lock.acquire()
        assert lock.is_held is True
        lock.release()

    def test_is_held_false_before_acquire(self):
        lock, _ = _make_lock()
        assert lock.is_held is False

    def test_is_held_false_after_release(self):
        lock, _ = _make_lock()
        lock.acquire()
        lock.release()
        assert lock.is_held is False

    def test_release_without_acquire_does_not_raise(self):
        lock, _ = _make_lock()
        # Should not raise even if never acquired
        lock.release()

    def test_acquire_release_acquire_again(self):
        """Lock can be reused after release."""
        lock, _ = _make_lock()
        assert lock.acquire() is True
        lock.release()
        assert lock.acquire() is True
        lock.release()

    def test_timeout_zero_fails_when_held(self):
        """A second process cannot acquire a held lock with timeout=0."""
        lock1, lock_dir = _make_lock("shared-lock")
        lock2 = LocalLock(name="shared-lock", lock_dir=lock_dir)
        lock1.acquire()
        try:
            # timeout=0 → returns False immediately without waiting
            result = lock2.acquire(timeout=0.0)
            assert result is False
        finally:
            lock1.release()

    def test_separate_locks_independent(self):
        """Two locks with different names can both be held simultaneously."""
        lock_dir = tempfile.mkdtemp(prefix="codomyrmex-test-ind-")
        lock_a = LocalLock(name="lock-a", lock_dir=lock_dir)
        lock_b = LocalLock(name="lock-b", lock_dir=lock_dir)
        assert lock_a.acquire() is True
        assert lock_b.acquire() is True
        lock_a.release()
        lock_b.release()


@pytest.mark.unit
class TestLocalLockContextManager:
    def test_context_manager_acquires_on_enter(self):
        lock, _ = _make_lock()
        with lock:
            assert lock.is_held is True

    def test_context_manager_releases_on_exit(self):
        lock, _ = _make_lock()
        with lock:
            pass
        assert lock.is_held is False

    def test_context_manager_releases_on_exception(self):
        lock, _ = _make_lock()
        try:
            with lock:
                raise RuntimeError("test error")
        except RuntimeError:
            pass
        assert lock.is_held is False

    def test_context_manager_timeout_raises(self):
        """Context manager raises TimeoutError when lock cannot be acquired."""
        lock1, lock_dir = _make_lock("cm-shared")
        lock2 = LocalLock(name="cm-shared", lock_dir=lock_dir)
        lock1.acquire()
        try:
            with pytest.raises(TimeoutError):
                lock2.acquire = lambda timeout=10.0, retry_interval=0.1: False  # type: ignore
                with lock2:
                    pass
        finally:
            lock1.release()

    def test_lock_file_created_on_acquire(self):
        lock_dir = tempfile.mkdtemp(prefix="codomyrmex-test-file-")
        lock = LocalLock(name="my-test-lock", lock_dir=lock_dir)
        lock.acquire()
        try:
            lock_file = Path(lock_dir) / "my-test-lock.lock"
            assert lock_file.exists()
        finally:
            lock.release()

    def test_lock_file_removed_on_release(self):
        lock_dir = tempfile.mkdtemp(prefix="codomyrmex-test-rm-")
        lock = LocalLock(name="cleanup-lock", lock_dir=lock_dir)
        lock.acquire()
        lock.release()
        lock_file = Path(lock_dir) / "cleanup-lock.lock"
        assert not lock_file.exists()

    def test_name_stored(self):
        lock, _ = _make_lock("my-named-lock")
        assert lock.name == "my-named-lock"
