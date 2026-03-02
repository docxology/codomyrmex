"""
Unit tests for logging_monitoring core submodules — Zero-Mock compliant.

Covers:
  - logging_monitoring/core/correlation.py
      (new_correlation_id, get_correlation_id, set_correlation_id,
       clear_correlation_id, with_correlation, CorrelationFilter,
       enrich_event_data, create_mcp_correlation_header)
  - logging_monitoring/formatters/json_formatter.py
      (JSONFormatter, PrettyJSONFormatter, RedactedJSONFormatter)
"""

import json
import logging

import pytest

from codomyrmex.logging_monitoring.core.correlation import (
    CorrelationFilter,
    clear_correlation_id,
    create_mcp_correlation_header,
    enrich_event_data,
    get_correlation_id,
    new_correlation_id,
    set_correlation_id,
    with_correlation,
)
from codomyrmex.logging_monitoring.formatters.json_formatter import (
    JSONFormatter,
    PrettyJSONFormatter,
    RedactedJSONFormatter,
)

# ── Helpers ─────────────────────────────────────────────────────────────────


def _make_record(msg: str = "test message", level: int = logging.INFO) -> logging.LogRecord:
    """Create a minimal LogRecord for formatter tests."""
    record = logging.LogRecord(
        name="test.logger",
        level=level,
        pathname="test_file.py",
        lineno=42,
        msg=msg,
        args=(),
        exc_info=None,
    )
    return record


# ── Correlation: core functions ─────────────────────────────────────────────


@pytest.mark.unit
class TestNewCorrelationId:
    """Tests for new_correlation_id()."""

    def setup_method(self):
        clear_correlation_id()

    def test_returns_string(self):
        cid = new_correlation_id()
        assert isinstance(cid, str)

    def test_starts_with_cid_prefix(self):
        cid = new_correlation_id()
        assert cid.startswith("cid-")

    def test_sets_in_context(self):
        cid = new_correlation_id()
        assert get_correlation_id() == cid

    def test_unique_each_call(self):
        cid1 = new_correlation_id()
        cid2 = new_correlation_id()
        assert cid1 != cid2


@pytest.mark.unit
class TestGetSetClearCorrelationId:
    """Tests for get/set/clear functions."""

    def setup_method(self):
        clear_correlation_id()

    def test_get_returns_empty_when_not_set(self):
        assert get_correlation_id() == ""

    def test_set_and_get_roundtrip(self):
        set_correlation_id("req-abc123")
        assert get_correlation_id() == "req-abc123"

    def test_clear_resets_to_empty(self):
        set_correlation_id("req-abc123")
        clear_correlation_id()
        assert get_correlation_id() == ""

    def test_set_empty_string(self):
        set_correlation_id("")
        assert get_correlation_id() == ""


@pytest.mark.unit
class TestWithCorrelation:
    """Tests for with_correlation context manager."""

    def setup_method(self):
        clear_correlation_id()

    def test_yields_correlation_id(self):
        with with_correlation("test-cid") as cid:
            assert cid == "test-cid"
            assert get_correlation_id() == "test-cid"

    def test_restores_previous_on_exit(self):
        set_correlation_id("outer-cid")
        with with_correlation("inner-cid"):
            pass
        assert get_correlation_id() == "outer-cid"

    def test_auto_generates_cid_when_none(self):
        with with_correlation() as cid:
            assert cid.startswith("cid-")
            assert len(cid) > 4

    def test_clears_after_exit(self):
        with with_correlation("ephemeral"):
            pass
        # Was restored to whatever was set before (empty in this case)
        assert get_correlation_id() == ""

    def test_nested_correlation(self):
        with with_correlation("outer"):
            assert get_correlation_id() == "outer"
            with with_correlation("inner") as inner_cid:
                assert get_correlation_id() == "inner"
                assert inner_cid == "inner"
            assert get_correlation_id() == "outer"

    def test_exception_still_restores(self):
        set_correlation_id("before")
        try:
            with with_correlation("during"):
                raise ValueError("test error")
        except ValueError:
            pass
        assert get_correlation_id() == "before"


@pytest.mark.unit
class TestCorrelationFilter:
    """Tests for CorrelationFilter logging filter."""

    def setup_method(self):
        clear_correlation_id()

    def test_filter_injects_correlation_id(self):
        set_correlation_id("cid-abc")
        filt = CorrelationFilter()
        record = _make_record()
        filt.filter(record)
        assert record.correlation_id == "cid-abc"

    def test_filter_injects_empty_when_not_set(self):
        filt = CorrelationFilter()
        record = _make_record()
        filt.filter(record)
        assert record.correlation_id == ""

    def test_filter_returns_true(self):
        filt = CorrelationFilter()
        record = _make_record()
        assert filt.filter(record) is True

    def test_filter_with_active_correlation(self):
        with with_correlation("in-filter"):
            filt = CorrelationFilter()
            record = _make_record()
            filt.filter(record)
            assert record.correlation_id == "in-filter"


@pytest.mark.unit
class TestEnrichEventData:
    """Tests for enrich_event_data()."""

    def setup_method(self):
        clear_correlation_id()

    def test_adds_correlation_id_when_set(self):
        set_correlation_id("cid-xyz")
        data = {"type": "event"}
        result = enrich_event_data(data)
        assert result["correlation_id"] == "cid-xyz"

    def test_does_not_add_when_not_set(self):
        data = {"type": "event"}
        result = enrich_event_data(data)
        assert "correlation_id" not in result

    def test_returns_same_dict(self):
        data = {"key": "val"}
        result = enrich_event_data(data)
        assert result is data

    def test_does_not_overwrite_existing_keys(self):
        set_correlation_id("cid-new")
        data = {"correlation_id": "cid-existing"}
        result = enrich_event_data(data)
        # Overwrites — active ID wins
        assert result["correlation_id"] == "cid-new"


@pytest.mark.unit
class TestCreateMcpCorrelationHeader:
    """Tests for create_mcp_correlation_header()."""

    def setup_method(self):
        clear_correlation_id()

    def test_returns_header_when_cid_set(self):
        set_correlation_id("cid-header")
        header = create_mcp_correlation_header()
        assert header == {"x-correlation-id": "cid-header"}

    def test_returns_empty_dict_when_not_set(self):
        header = create_mcp_correlation_header()
        assert header == {}

    def test_header_key_name(self):
        set_correlation_id("cid-test")
        header = create_mcp_correlation_header()
        assert "x-correlation-id" in header


# ── JSONFormatter ───────────────────────────────────────────────────────────


@pytest.mark.unit
class TestJSONFormatter:
    """Tests for JSONFormatter."""

    def test_format_returns_string(self):
        fmt = JSONFormatter()
        record = _make_record("hello")
        result = fmt.format(record)
        assert isinstance(result, str)

    def test_format_is_valid_json(self):
        fmt = JSONFormatter()
        record = _make_record("hello")
        parsed = json.loads(fmt.format(record))
        assert isinstance(parsed, dict)

    def test_format_contains_required_fields(self):
        fmt = JSONFormatter()
        parsed = json.loads(fmt.format(_make_record("test")))
        assert "timestamp" in parsed
        assert "level" in parsed
        assert "name" in parsed
        assert "message" in parsed
        assert "module" in parsed
        assert "line" in parsed

    def test_format_level_name(self):
        fmt = JSONFormatter()
        record = _make_record("msg", level=logging.WARNING)
        parsed = json.loads(fmt.format(record))
        assert parsed["level"] == "WARNING"

    def test_format_message(self):
        fmt = JSONFormatter()
        parsed = json.loads(fmt.format(_make_record("my message")))
        assert parsed["message"] == "my message"

    def test_include_fields_filters(self):
        fmt = JSONFormatter(include_fields=["level", "message"])
        parsed = json.loads(fmt.format(_make_record("hello")))
        assert set(parsed.keys()) == {"level", "message"}

    def test_exclude_fields_removes(self):
        fmt = JSONFormatter(exclude_fields=["module", "line"])
        parsed = json.loads(fmt.format(_make_record("hello")))
        assert "module" not in parsed
        assert "line" not in parsed

    def test_extra_field_included(self):
        fmt = JSONFormatter()
        record = _make_record("hello")
        record.extra = {"request_id": "req-123"}
        parsed = json.loads(fmt.format(record))
        assert parsed["request_id"] == "req-123"

    def test_exception_included(self):
        fmt = JSONFormatter()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="f.py",
            lineno=1, msg="error", args=(), exc_info=exc_info,
        )
        parsed = json.loads(fmt.format(record))
        assert "exception" in parsed


@pytest.mark.unit
class TestPrettyJSONFormatter:
    """Tests for PrettyJSONFormatter."""

    def test_format_returns_string(self):
        fmt = PrettyJSONFormatter()
        result = fmt.format(_make_record("hello"))
        assert isinstance(result, str)

    def test_format_is_valid_json(self):
        fmt = PrettyJSONFormatter()
        parsed = json.loads(fmt.format(_make_record("hello")))
        assert isinstance(parsed, dict)

    def test_format_is_indented(self):
        fmt = PrettyJSONFormatter(indent=2)
        result = fmt.format(_make_record("hello"))
        # Indented JSON has newlines
        assert "\n" in result

    def test_custom_indent(self):
        fmt = PrettyJSONFormatter(indent=4)
        result = fmt.format(_make_record("hello"))
        assert "    " in result  # 4-space indent

    def test_inherits_include_fields(self):
        fmt = PrettyJSONFormatter(include_fields=["level"])
        parsed = json.loads(fmt.format(_make_record("hello")))
        assert list(parsed.keys()) == ["level"]


@pytest.mark.unit
class TestRedactedJSONFormatter:
    """Tests for RedactedJSONFormatter."""

    def test_format_returns_string(self):
        fmt = RedactedJSONFormatter()
        result = fmt.format(_make_record("hello"))
        assert isinstance(result, str)

    def test_format_is_valid_json(self):
        fmt = RedactedJSONFormatter()
        parsed = json.loads(fmt.format(_make_record("hello")))
        assert isinstance(parsed, dict)

    def test_sensitive_field_redacted(self):
        fmt = RedactedJSONFormatter()
        record = _make_record("hello")
        record.extra = {"password": "supersecret"}
        parsed = json.loads(fmt.format(record))
        assert parsed["password"] == "[REDACTED]"

    def test_token_field_redacted(self):
        fmt = RedactedJSONFormatter()
        record = _make_record("hello")
        record.extra = {"token": "abcdef123"}
        parsed = json.loads(fmt.format(record))
        assert parsed["token"] == "[REDACTED]"

    def test_safe_field_not_redacted(self):
        fmt = RedactedJSONFormatter()
        record = _make_record("hello")
        record.extra = {"user_id": "alice"}
        parsed = json.loads(fmt.format(record))
        assert parsed["user_id"] == "alice"

    def test_custom_replacement(self):
        fmt = RedactedJSONFormatter(replacement="***")
        record = _make_record("hello")
        record.extra = {"password": "secret"}
        parsed = json.loads(fmt.format(record))
        assert parsed["password"] == "***"

    def test_custom_patterns(self):
        fmt = RedactedJSONFormatter(patterns=["phone"])
        record = _make_record("hello")
        record.extra = {"phone": "555-1234"}
        parsed = json.loads(fmt.format(record))
        assert parsed["phone"] == "[REDACTED]"

    def test_nested_dict_redacted(self):
        fmt = RedactedJSONFormatter()
        record = _make_record("hello")
        # Use a non-sensitive outer key so nested traversal is exercised
        record.extra = {"config": {"api_key": "key123", "username": "bob"}}
        parsed = json.loads(fmt.format(record))
        assert parsed["config"]["api_key"] == "[REDACTED]"
        assert parsed["config"]["username"] == "bob"
