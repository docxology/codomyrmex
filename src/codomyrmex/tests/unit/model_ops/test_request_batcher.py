"""
Unit tests for model_ops.optimization.batcher — Zero-Mock compliant.

Covers: RequestBatcher (start/stop, submit_sync, submit_async,
_get_request_id, _collect_batch, _process_batch, stats).
"""

import time

import pytest

from codomyrmex.model_ops.optimization.batcher import RequestBatcher

# ── Helpers ───────────────────────────────────────────────────────────


def _identity_processor(inputs: list) -> list:
    """Returns inputs unchanged."""
    return inputs


def _double_processor(inputs: list) -> list:
    """Doubles each numeric input."""
    return [x * 2 for x in inputs]


def _error_processor(inputs: list) -> list:
    """Always raises RuntimeError."""
    raise RuntimeError("processing failed")


# ── Construction ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestRequestBatcherConstruction:
    def test_default_params(self):
        b = RequestBatcher()
        assert b.max_batch_size == 32
        assert b.timeout_ms == 100.0
        assert b.processor is None

    def test_custom_params(self):
        b = RequestBatcher(max_batch_size=8, timeout_ms=50.0, processor=_identity_processor)
        assert b.max_batch_size == 8
        assert b.timeout_ms == 50.0
        assert b.processor is _identity_processor

    def test_starts_not_running(self):
        b = RequestBatcher()
        assert b._running is False
        assert b._thread is None


# ── Start / Stop ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestRequestBatcherStartStop:
    def test_start_sets_running(self):
        b = RequestBatcher(processor=_identity_processor, timeout_ms=10)
        b.start()
        assert b._running is True
        assert b._thread is not None
        b.stop()

    def test_start_idempotent(self):
        b = RequestBatcher(processor=_identity_processor, timeout_ms=10)
        b.start()
        thread1 = b._thread
        b.start()
        thread2 = b._thread
        assert thread1 is thread2
        b.stop()

    def test_stop_sets_not_running(self):
        b = RequestBatcher(processor=_identity_processor, timeout_ms=10)
        b.start()
        b.stop()
        assert b._running is False


# ── Request ID generation ─────────────────────────────────────────────


@pytest.mark.unit
class TestRequestIdGeneration:
    def test_unique_ids(self):
        b = RequestBatcher()
        ids = [b._get_request_id() for _ in range(5)]
        assert len(set(ids)) == 5

    def test_id_prefix(self):
        b = RequestBatcher()
        req_id = b._get_request_id()
        assert req_id.startswith("req_")

    def test_counter_increments(self):
        b = RequestBatcher()
        b._get_request_id()
        b._get_request_id()
        assert b._counter == 2


# ── submit_sync ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestSubmitSync:
    def test_submit_sync_returns_result(self):
        b = RequestBatcher(
            max_batch_size=1,
            timeout_ms=10,
            processor=_double_processor,
        )
        b.start()
        result = b.submit_sync(5, timeout=5.0)
        b.stop()
        assert result == 10

    def test_submit_sync_increments_total_requests(self):
        b = RequestBatcher(
            max_batch_size=1,
            timeout_ms=10,
            processor=_identity_processor,
        )
        b.start()
        b.submit_sync("hello", timeout=5.0)
        b.stop()
        assert b._total_requests == 1

    def test_submit_sync_string_input(self):
        b = RequestBatcher(
            max_batch_size=1,
            timeout_ms=10,
            processor=_identity_processor,
        )
        b.start()
        result = b.submit_sync("test_value", timeout=5.0)
        b.stop()
        assert result == "test_value"


# ── submit_async ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestSubmitAsync:
    def test_submit_async_returns_future(self):
        b = RequestBatcher(
            max_batch_size=1,
            timeout_ms=10,
            processor=_identity_processor,
        )
        b.start()
        future = b.submit_async("data")
        result = future.result(timeout=5.0)
        b.stop()
        assert result == "data"

    def test_submit_async_multiple(self):
        b = RequestBatcher(
            max_batch_size=4,
            timeout_ms=50,
            processor=_double_processor,
        )
        b.start()
        futures = [b.submit_async(i) for i in range(4)]
        results = [f.result(timeout=5.0) for f in futures]
        b.stop()
        assert results == [0, 2, 4, 6]

    def test_submit_async_increments_counter(self):
        b = RequestBatcher(
            max_batch_size=1,
            timeout_ms=10,
            processor=_identity_processor,
        )
        b.start()
        b.submit_async("a")
        time.sleep(0.1)
        b.stop()
        assert b._total_requests == 1


# ── Error handling ────────────────────────────────────────────────────


@pytest.mark.unit
class TestBatcherErrorHandling:
    def test_processor_error_propagates_to_future(self):
        b = RequestBatcher(
            max_batch_size=1,
            timeout_ms=10,
            processor=_error_processor,
        )
        b.start()
        future = b.submit_async("data")
        with pytest.raises(RuntimeError, match="processing failed"):
            future.result(timeout=5.0)
        b.stop()


# ── _process_batch without processor ─────────────────────────────────


@pytest.mark.unit
class TestProcessBatchNoProcessor:
    def test_no_processor_does_not_set_future(self):
        b = RequestBatcher(processor=None)
        from concurrent.futures import Future
        future = Future()
        b._process_batch([(b._get_request_id(), "data", future)])
        # Future should not be resolved
        assert not future.done()


# ── Stats ─────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestBatcherStats:
    def test_initial_stats_zero(self):
        b = RequestBatcher()
        s = b.stats
        assert s["total_requests"] == 0
        assert s["total_batches"] == 0
        assert s["avg_batch_size"] == 0

    def test_stats_after_processing(self):
        b = RequestBatcher(
            max_batch_size=2,
            timeout_ms=20,
            processor=_identity_processor,
        )
        b.start()
        b.submit_sync("a", timeout=5.0)
        b.stop()
        s = b.stats
        assert s["total_batches"] >= 1
        assert s["avg_batch_size"] >= 1

    def test_stats_avg_batch_size_no_batches(self):
        b = RequestBatcher()
        assert b.stats["avg_batch_size"] == 0
