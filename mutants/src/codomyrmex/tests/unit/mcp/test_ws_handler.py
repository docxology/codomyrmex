"""Tests for WebSocketLogHandler (Stream 6).

Verifies:
- Handler initialization and configuration
- Log record formatting to dict
- Queue backpressure (drop oldest when full)
- Client add/remove and broadcast
- Correlation ID and exception info threading
"""

from __future__ import annotations

import asyncio
import logging

import pytest

from codomyrmex.logging_monitoring.ws_handler import WebSocketLogHandler


# ── Initialization ────────────────────────────────────────────────────


class TestInitialization:
    """Verify handler setup."""

    def test_handler_default_queue_size(self) -> None:
        handler = WebSocketLogHandler()
        assert handler._max_queue_size == 1000

    def test_handler_custom_queue_size(self) -> None:
        handler = WebSocketLogHandler(max_queue_size=50)
        assert handler._max_queue_size == 50

    def test_handler_is_logging_handler(self) -> None:
        handler = WebSocketLogHandler()
        assert isinstance(handler, logging.Handler)


# ── Record formatting ────────────────────────────────────────────────


class TestRecordFormatting:
    """Verify log records are formatted as dicts."""

    def test_basic_record_format(self) -> None:
        handler = WebSocketLogHandler()
        logger = logging.getLogger("test.ws_handler")
        logger.setLevel(logging.DEBUG)

        record = logger.makeRecord(
            "test.ws_handler", logging.INFO, "test.py", 42,
            "hello world", (), None,
        )
        entry = handler._format_record(record)

        assert entry["level"] == "INFO"
        assert entry["logger"] == "test.ws_handler"
        assert "hello world" in entry["message"]
        assert entry["line"] == 42

    def test_correlation_id_included(self) -> None:
        handler = WebSocketLogHandler()
        logger = logging.getLogger("test.ws_handler.corr")
        record = logger.makeRecord(
            "test", logging.INFO, "test.py", 1, "msg", (), None,
        )
        record.correlation_id = "abc-123"

        entry = handler._format_record(record)
        assert entry["correlation_id"] == "abc-123"

    def test_exception_info_included(self) -> None:
        handler = WebSocketLogHandler()
        logger = logging.getLogger("test.ws_handler.exc")
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            import sys
            record = logger.makeRecord(
                "test", logging.ERROR, "test.py", 1, "err", (),
                sys.exc_info(),
            )

        entry = handler._format_record(record)
        assert entry["exception"]["type"] == "RuntimeError"
        assert "boom" in entry["exception"]["message"]


# ── Queue backpressure ────────────────────────────────────────────────


class TestBackpressure:
    """Verify oldest entries are dropped when queue is full."""

    def test_drop_oldest_on_overflow(self) -> None:
        handler = WebSocketLogHandler(max_queue_size=3)
        logger = logging.getLogger("test.ws_handler.bp")

        for i in range(5):
            record = logger.makeRecord(
                "test", logging.INFO, "test.py", 1, f"msg_{i}", (), None,
            )
            handler.emit(record)

        # Queue holds at most 3 entries
        assert handler._queue.qsize() <= 3
        assert handler.dropped_count >= 2

    def test_no_drops_within_limit(self) -> None:
        handler = WebSocketLogHandler(max_queue_size=10)
        logger = logging.getLogger("test.ws_handler.nodrops")

        for i in range(5):
            record = logger.makeRecord(
                "test", logging.INFO, "test.py", 1, f"msg_{i}", (), None,
            )
            handler.emit(record)

        assert handler._queue.qsize() == 5
        assert handler.dropped_count == 0


# ── Client management ────────────────────────────────────────────────


class TestClientManagement:
    """Verify client add/remove and broadcast."""

    def test_add_and_remove_client(self) -> None:
        handler = WebSocketLogHandler()
        q = handler.add_client()
        assert handler.client_count == 1
        handler.remove_client(q)
        assert handler.client_count == 0

    def test_remove_nonexistent_client(self) -> None:
        handler = WebSocketLogHandler()
        fake_queue: asyncio.Queue = asyncio.Queue()
        handler.remove_client(fake_queue)  # No error
        assert handler.client_count == 0

    def test_broadcast_to_all_clients(self) -> None:
        handler = WebSocketLogHandler()
        q1 = handler.add_client()
        q2 = handler.add_client()

        logger = logging.getLogger("test.ws_handler.broadcast")
        record = logger.makeRecord(
            "test", logging.INFO, "test.py", 1, "broadcast_msg", (), None,
        )
        handler.emit(record)

        assert q1.qsize() == 1
        assert q2.qsize() == 1

    def test_client_backpressure(self) -> None:
        handler = WebSocketLogHandler(max_queue_size=2)
        q = handler.add_client()

        logger = logging.getLogger("test.ws_handler.clientbp")
        for i in range(5):
            record = logger.makeRecord(
                "test", logging.INFO, "test.py", 1, f"msg_{i}", (), None,
            )
            handler.emit(record)

        # Client queue holds at most 2 entries
        assert q.qsize() <= 2


# ── Async stream ──────────────────────────────────────────────────────


class TestAsyncStream:
    """Verify async stream generator."""

    @pytest.mark.asyncio
    async def test_stream_yields_entries(self) -> None:
        handler = WebSocketLogHandler()
        logger = logging.getLogger("test.ws_handler.stream")

        # Emit a record
        record = logger.makeRecord(
            "test", logging.INFO, "test.py", 1, "stream_test", (), None,
        )
        handler.emit(record)

        # Stream should yield the entry
        gen = handler.stream()
        entry = await asyncio.wait_for(gen.__anext__(), timeout=1.0)
        assert "stream_test" in entry["message"]
