"""Tests for correlation ID propagation.

Validates the contextvars-based correlation ID system for threading
identifiers through MCP → EventBus → logging → audit.
"""

import logging

import pytest

from codomyrmex.logging_monitoring.correlation import (
    new_correlation_id,
    get_correlation_id,
    set_correlation_id,
    clear_correlation_id,
    with_correlation,
    CorrelationFilter,
    enrich_event_data,
    create_mcp_correlation_header,
)


class TestCorrelationId:
    """Core correlation ID operations."""

    def test_new_correlation_id_format(self):
        cid = new_correlation_id()
        assert cid.startswith("cid-")
        assert len(cid) == 16  # "cid-" + 12 hex chars

    def test_get_returns_current(self):
        cid = new_correlation_id()
        assert get_correlation_id() == cid

    def test_set_explicit(self):
        set_correlation_id("test-123")
        assert get_correlation_id() == "test-123"

    def test_clear(self):
        new_correlation_id()
        clear_correlation_id()
        assert get_correlation_id() == ""

    def test_unique_ids(self):
        ids = {new_correlation_id() for _ in range(100)}
        assert len(ids) == 100

    def teardown_method(self):
        clear_correlation_id()


class TestWithCorrelation:
    """Context manager tests."""

    def test_auto_generate(self):
        with with_correlation() as cid:
            assert cid.startswith("cid-")
            assert get_correlation_id() == cid
        assert get_correlation_id() == ""

    def test_explicit_id(self):
        with with_correlation("my-trace-42") as cid:
            assert cid == "my-trace-42"
            assert get_correlation_id() == "my-trace-42"
        assert get_correlation_id() == ""

    def test_nested_contexts(self):
        with with_correlation("outer") as outer:
            assert get_correlation_id() == "outer"
            with with_correlation("inner") as inner:
                assert get_correlation_id() == "inner"
            assert get_correlation_id() == "outer"
        assert get_correlation_id() == ""


class TestCorrelationFilter:
    """Logging filter integration tests."""

    def test_filter_injects_id(self):
        filt = CorrelationFilter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)

        set_correlation_id("log-trace-1")
        filt.filter(record)

        assert record.correlation_id == "log-trace-1"  # type: ignore[attr-defined]
        clear_correlation_id()

    def test_filter_empty_when_unset(self):
        filt = CorrelationFilter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        clear_correlation_id()

        filt.filter(record)

        assert record.correlation_id == ""  # type: ignore[attr-defined]

    def test_filter_always_returns_true(self):
        filt = CorrelationFilter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        assert filt.filter(record) is True


class TestEventIntegration:
    """EventBus data enrichment."""

    def test_enrich_adds_id(self):
        set_correlation_id("evt-42")
        data = enrich_event_data({"tool": "analyze"})
        assert data["correlation_id"] == "evt-42"
        assert data["tool"] == "analyze"
        clear_correlation_id()

    def test_enrich_skips_when_unset(self):
        clear_correlation_id()
        data = enrich_event_data({"tool": "analyze"})
        assert "correlation_id" not in data


class TestMcpIntegration:
    """MCP metadata header generation."""

    def test_header_with_id(self):
        set_correlation_id("mcp-trace-7")
        headers = create_mcp_correlation_header()
        assert headers == {"x-correlation-id": "mcp-trace-7"}
        clear_correlation_id()

    def test_header_empty_when_unset(self):
        clear_correlation_id()
        headers = create_mcp_correlation_header()
        assert headers == {}
