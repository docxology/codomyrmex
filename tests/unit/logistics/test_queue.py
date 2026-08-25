"""Test that explicitly requesting an unavailable backend raises RequestedBackendUnavailable."""

import pytest

from codomyrmex.exceptions import RequestedBackendUnavailable
from codomyrmex.logistics.task.queue import Queue


def test_redis_backend_raises_when_unavailable():
    """Requesting redis backend must raise RequestedBackendUnavailable."""
    with pytest.raises(RequestedBackendUnavailable) as excinfo:
        Queue(backend="redis")
    assert "redis" in str(excinfo.value).lower()


def test_unknown_backend_falls_back():
    """An unknown backend name should still fall back to in-memory (not raise)."""
    q = Queue(backend="nonexistent")
    assert q._queue is not None


def test_in_memory_backend_works():
    """Default in-memory backend should work without error."""
    q = Queue(backend="in_memory")
    assert q._queue is not None
