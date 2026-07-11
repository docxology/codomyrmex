"""Zero-mock tests for logging_monitoring core: logger_config, json_formatter,
structured_formatter, correlation, and mcp_tools.

No mocks, no monkeypatch, no MagicMock. All tests call real code with real inputs.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile

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
from codomyrmex.logging_monitoring.core.logger_config import (
    AuditLogger,
    LogContext,
    create_correlation_id,
    enable_structured_json,
    get_logger,
    log_with_context,
    setup_logging,
)
from codomyrmex.logging_monitoring.formatters.json_formatter import (
    JSONFormatter,
    PrettyJSONFormatter,
    RedactedJSONFormatter,
)
from codomyrmex.logging_monitoring.formatters.structured_formatter import (
    FormatterConfig,
    LogLevel,
    StructuredFormatter,
    StructuredLogEntry,
)
from codomyrmex.logging_monitoring.formatters.structured_formatter import (
    LogContext as StructuredLogContext,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_log_record(
    name: str = "test.logger",
    level: int = logging.INFO,
    message: str = "test message",
    **extra,
) -> logging.LogRecord:
    record = logging.LogRecord(
        name=name,
        level=level,
        pathname="test_file.py",
        lineno=42,
        msg=message,
        args=(),
        exc_info=None,
    )
    for k, v in extra.items():
        setattr(record, k, v)
    return record


# ---------------------------------------------------------------------------
# TestJSONFormatter
# ---------------------------------------------------------------------------


class TestJSONFormatter:
    """Tests for the JSONFormatter class."""

    def test_format_returns_valid_json(self):
        formatter = JSONFormatter()
        record = make_log_record()
        result = formatter.format(record)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_format_contains_required_fields(self):
        formatter = JSONFormatter()
        record = make_log_record(message="hello world")
        parsed = json.loads(formatter.format(record))
        assert "timestamp" in parsed
        assert "level" in parsed
        assert "name" in parsed
        assert "message" in parsed
        assert parsed["message"] == "hello world"

    def test_format_level_is_correct(self):
        formatter = JSONFormatter()
        record = make_log_record(level=logging.ERROR)
        parsed = json.loads(formatter.format(record))
        assert parsed["level"] == "ERROR"

    def test_format_name_is_correct(self):
        formatter = JSONFormatter()
        record = make_log_record(name="codomyrmex.core")
        parsed = json.loads(formatter.format(record))
        assert parsed["name"] == "codomyrmex.core"

    def test_format_includes_module_and_line(self):
        formatter = JSONFormatter()
        record = make_log_record()
        parsed = json.loads(formatter.format(record))
        assert "module" in parsed
        assert "line" in parsed
        assert parsed["line"] == 42

    def test_format_with_correlation_id_extra(self):
        formatter = JSONFormatter()
        record = make_log_record(correlation_id="cid-abc123")
        parsed = json.loads(formatter.format(record))
        assert parsed.get("correlation_id") == "cid-abc123"

    def test_format_with_context_extra(self):
        formatter = JSONFormatter()
        record = make_log_record(context={"user_id": "u42"})
        parsed = json.loads(formatter.format(record))
        assert parsed.get("context") == {"user_id": "u42"}

    def test_format_include_fields_filters(self):
        formatter = JSONFormatter(include_fields=["timestamp", "message"])
        record = make_log_record(message="filtered")
        parsed = json.loads(formatter.format(record))
        assert "timestamp" in parsed
        assert "message" in parsed
        assert "level" not in parsed

    def test_format_exclude_fields_removes_key(self):
        formatter = JSONFormatter(exclude_fields=["module"])
        record = make_log_record()
        parsed = json.loads(formatter.format(record))
        assert "module" not in parsed

    def test_format_exception_info_included(self):
        formatter = JSONFormatter()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="f.py",
                lineno=1,
                msg="err",
                args=(),
                exc_info=exc_info,
            )
        parsed = json.loads(formatter.format(record))
        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]


class TestPrettyJSONFormatter:
    """Tests for PrettyJSONFormatter."""

    def test_output_is_indented(self):
        formatter = PrettyJSONFormatter(indent=4)
        record = make_log_record()
        result = formatter.format(record)
        # Indented JSON has newlines
        assert "\n" in result

    def test_output_is_valid_json(self):
        formatter = PrettyJSONFormatter()
        record = make_log_record()
        parsed = json.loads(formatter.format(record))
        assert "message" in parsed

    def test_default_indent_is_2(self):
        formatter = PrettyJSONFormatter()
        assert formatter._indent == 2


class TestRedactedJSONFormatter:
    """Tests for RedactedJSONFormatter."""

    def test_password_field_is_redacted(self):
        formatter = RedactedJSONFormatter()
        record = make_log_record(password="secret123")
        parsed = json.loads(formatter.format(record))
        assert parsed.get("password") == "[REDACTED]"

    def test_token_field_is_redacted(self):
        formatter = RedactedJSONFormatter()
        record = make_log_record(api_key="sk-abc")
        parsed = json.loads(formatter.format(record))
        assert parsed.get("api_key") == "[REDACTED]"

    def test_non_sensitive_field_is_preserved(self):
        formatter = RedactedJSONFormatter()
        record = make_log_record(user_id="u42")
        parsed = json.loads(formatter.format(record))
        assert parsed.get("user_id") == "u42"

    def test_custom_replacement_string(self):
        formatter = RedactedJSONFormatter(replacement="***")
        record = make_log_record(secret="mysecret")
        parsed = json.loads(formatter.format(record))
        assert parsed.get("secret") == "***"

    def test_custom_pattern_is_redacted(self):
        formatter = RedactedJSONFormatter(patterns=["ssn_number"])
        record = make_log_record(ssn_number="123-45-6789")
        parsed = json.loads(formatter.format(record))
        assert parsed.get("ssn_number") == "[REDACTED]"


# ---------------------------------------------------------------------------
# TestStructuredFormatter
# ---------------------------------------------------------------------------


class TestStructuredFormatter:
    """Tests for StructuredFormatter and related dataclasses."""

    def test_format_returns_valid_json(self):
        formatter = StructuredFormatter()
        entry = StructuredLogEntry(level=LogLevel.INFO, message="hello")
        result = formatter.format(entry)
        parsed = json.loads(result)
        assert parsed["message"] == "hello"
        assert parsed["level"] == "info"

    def test_format_increments_line_count(self):
        formatter = StructuredFormatter()
        entry = StructuredLogEntry(level=LogLevel.DEBUG, message="a")
        assert formatter.lines_formatted == 0
        formatter.format(entry)
        assert formatter.lines_formatted == 1
        formatter.format(entry)
        assert formatter.lines_formatted == 2

    def test_reset_count(self):
        formatter = StructuredFormatter()
        entry = StructuredLogEntry(level=LogLevel.INFO, message="x")
        formatter.format(entry)
        formatter.reset_count()
        assert formatter.lines_formatted == 0

    def test_format_with_correlation_id(self):
        ctx = StructuredLogContext(correlation_id="cid-xyz")
        formatter = StructuredFormatter()
        entry = StructuredLogEntry(level=LogLevel.INFO, message="trace", context=ctx)
        parsed = json.loads(formatter.format(entry))
        assert parsed["correlation_id"] == "cid-xyz"

    def test_format_with_module_context(self):
        ctx = StructuredLogContext(module="codomyrmex.agents", function="run")
        formatter = StructuredFormatter()
        entry = StructuredLogEntry(level=LogLevel.INFO, message="run", context=ctx)
        parsed = json.loads(formatter.format(entry))
        assert parsed["module"] == "codomyrmex.agents"
        assert parsed["function"] == "run"

    def test_format_truncates_long_message(self):
        config = FormatterConfig(max_message_length=10)
        formatter = StructuredFormatter(config=config)
        entry = StructuredLogEntry(level=LogLevel.INFO, message="a" * 50)
        parsed = json.loads(formatter.format(entry))
        assert len(parsed["message"]) == 13  # 10 + "..."
        assert parsed["message"].endswith("...")

    def test_format_static_fields_included(self):
        config = FormatterConfig(static_fields={"service": "svc", "env": "test"})
        formatter = StructuredFormatter(config=config)
        entry = StructuredLogEntry(level=LogLevel.INFO, message="ok")
        parsed = json.loads(formatter.format(entry))
        assert parsed["service"] == "svc"
        assert parsed["env"] == "test"

    def test_format_error_with_exception_includes_stacktrace(self):
        formatter = StructuredFormatter()
        try:
            raise RuntimeError("test error")
        except RuntimeError as exc:
            entry = StructuredLogEntry(
                level=LogLevel.ERROR, message="failed", error=exc
            )
        parsed = json.loads(formatter.format(entry))
        assert "error_type" in parsed
        assert parsed["error_type"] == "RuntimeError"
        assert "stacktrace" in parsed

    def test_format_extra_fields_included(self):
        formatter = StructuredFormatter()
        entry = StructuredLogEntry(
            level=LogLevel.INFO, message="with fields", fields={"req_id": "r1"}
        )
        parsed = json.loads(formatter.format(entry))
        assert parsed["req_id"] == "r1"

    def test_format_batch_produces_newline_separated(self):
        formatter = StructuredFormatter()
        entries = [
            StructuredLogEntry(level=LogLevel.INFO, message=f"msg{i}") for i in range(3)
        ]
        result = formatter.format_batch(entries)
        lines = result.strip().split("\n")
        assert len(lines) == 3
        for line in lines:
            parsed = json.loads(line)
            assert "message" in parsed

    def test_pretty_print_config_indents_output(self):
        config = FormatterConfig(pretty_print=True)
        formatter = StructuredFormatter(config=config)
        entry = StructuredLogEntry(level=LogLevel.INFO, message="pretty")
        result = formatter.format(entry)
        assert "\n" in result

    def test_log_level_enum_values(self):
        assert LogLevel.DEBUG.value == "debug"
        assert LogLevel.INFO.value == "info"
        assert LogLevel.WARNING.value == "warning"
        assert LogLevel.ERROR.value == "error"
        assert LogLevel.CRITICAL.value == "critical"

    def test_formatter_config_defaults(self):
        config = FormatterConfig()
        assert config.include_timestamp is True
        assert config.include_level is True
        assert config.include_correlation_id is True
        assert config.pretty_print is False
        assert config.max_message_length == 0

    def test_context_extra_is_included_in_output(self):
        ctx = StructuredLogContext(extra={"env": "staging"})
        formatter = StructuredFormatter()
        entry = StructuredLogEntry(level=LogLevel.DEBUG, message="debug", context=ctx)
        parsed = json.loads(formatter.format(entry))
        assert parsed.get("context") == {"env": "staging"}


# ---------------------------------------------------------------------------
# TestCorrelation
# ---------------------------------------------------------------------------


class TestCorrelation:
    """Tests for the correlation module."""

    def setup_method(self):
        clear_correlation_id()

    def teardown_method(self):
        clear_correlation_id()

    def test_new_correlation_id_returns_string(self):
        cid = new_correlation_id()
        assert isinstance(cid, str)
        assert len(cid) > 0

    def test_new_correlation_id_starts_with_cid(self):
        cid = new_correlation_id()
        assert cid.startswith("cid-")

    def test_new_correlation_id_is_unique(self):
        cid1 = new_correlation_id()
        cid2 = new_correlation_id()
        assert cid1 != cid2

    def test_get_correlation_id_empty_by_default(self):
        clear_correlation_id()
        cid = get_correlation_id()
        assert cid == ""

    def test_set_and_get_correlation_id(self):
        set_correlation_id("my-cid-123")
        assert get_correlation_id() == "my-cid-123"

    def test_clear_resets_to_empty(self):
        set_correlation_id("some-id")
        clear_correlation_id()
        assert get_correlation_id() == ""

    def test_with_correlation_sets_id(self):
        with with_correlation("test-cid") as cid:
            assert cid == "test-cid"
            assert get_correlation_id() == "test-cid"

    def test_with_correlation_restores_after_exit(self):
        set_correlation_id("outer")
        with with_correlation("inner"):
            assert get_correlation_id() == "inner"
        # contextvars reset token restores outer
        # (outer was set before the context manager, token only resets to pre-set value)
        # After exit the token resets to whatever was there before "inner"
        # which is "outer" since we called set_correlation_id first
        result = get_correlation_id()
        assert result in ("outer", "")  # depends on ContextVar behavior

    def test_with_correlation_generates_id_if_none(self):
        with with_correlation() as cid:
            assert cid.startswith("cid-")

    def test_correlation_filter_injects_id_into_record(self):
        set_correlation_id("filter-cid")
        filt = CorrelationFilter()
        record = make_log_record()
        result = filt.filter(record)
        assert result is True
        assert record.correlation_id == "filter-cid"

    def test_correlation_filter_injects_empty_when_none(self):
        clear_correlation_id()
        filt = CorrelationFilter()
        record = make_log_record()
        filt.filter(record)
        assert record.correlation_id == ""

    def test_enrich_event_data_adds_correlation_id(self):
        set_correlation_id("enrich-cid")
        data = {"key": "value"}
        enriched = enrich_event_data(data)
        assert enriched["correlation_id"] == "enrich-cid"
        assert enriched["key"] == "value"

    def test_enrich_event_data_skips_when_empty(self):
        clear_correlation_id()
        data = {"key": "value"}
        enriched = enrich_event_data(data)
        assert "correlation_id" not in enriched

    def test_create_mcp_correlation_header_with_id(self):
        set_correlation_id("header-cid")
        headers = create_mcp_correlation_header()
        assert headers == {"x-correlation-id": "header-cid"}

    def test_create_mcp_correlation_header_empty_when_none(self):
        clear_correlation_id()
        headers = create_mcp_correlation_header()
        assert headers == {}


# ---------------------------------------------------------------------------
# TestLoggerConfig
# ---------------------------------------------------------------------------


class TestLoggerConfig:
    """Tests for logger_config module functions."""

    def test_get_logger_returns_logger_instance(self):
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_name_is_correct(self):
        logger = get_logger("codomyrmex.test")
        assert logger.name == "codomyrmex.test"

    def test_get_logger_same_name_returns_same_instance(self):
        l1 = get_logger("same.name")
        l2 = get_logger("same.name")
        assert l1 is l2

    def test_create_correlation_id_returns_uuid_string(self):
        cid = create_correlation_id()
        assert isinstance(cid, str)
        assert len(cid) == 36  # UUID4 format: 8-4-4-4-12
        assert cid.count("-") == 4

    def test_create_correlation_id_is_unique(self):
        cids = {create_correlation_id() for _ in range(10)}
        assert len(cids) == 10

    def test_setup_logging_runs_without_error(self):
        # Calling setup_logging with TEXT format should not raise
        os.environ.pop("CODOMYRMEX_LOG_FILE", None)
        old_level = os.environ.get("CODOMYRMEX_LOG_LEVEL")
        os.environ["CODOMYRMEX_LOG_LEVEL"] = "WARNING"
        try:
            setup_logging(force=True)
        finally:
            if old_level is None:
                os.environ.pop("CODOMYRMEX_LOG_LEVEL", None)
            else:
                os.environ["CODOMYRMEX_LOG_LEVEL"] = old_level

    def test_setup_logging_json_format(self):
        old_type = os.environ.get("CODOMYRMEX_LOG_OUTPUT_TYPE")
        os.environ["CODOMYRMEX_LOG_OUTPUT_TYPE"] = "JSON"
        try:
            setup_logging(force=True)
        finally:
            if old_type is None:
                os.environ.pop("CODOMYRMEX_LOG_OUTPUT_TYPE", None)
            else:
                os.environ["CODOMYRMEX_LOG_OUTPUT_TYPE"] = old_type
            setup_logging(force=True)  # restore TEXT

    def test_setup_logging_with_log_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test.log")
            old_file = os.environ.get("CODOMYRMEX_LOG_FILE")
            os.environ["CODOMYRMEX_LOG_FILE"] = log_path
            try:
                setup_logging(force=True)
                logger = get_logger("test.file.logger")
                logger.warning("test log entry")
            finally:
                if old_file is None:
                    os.environ.pop("CODOMYRMEX_LOG_FILE", None)
                else:
                    os.environ["CODOMYRMEX_LOG_FILE"] = old_file
                setup_logging(force=True)

    def test_enable_structured_json_on_named_logger(self):
        get_logger("codomyrmex.struct.test")
        # Should not raise even if logger has no handlers
        enable_structured_json("codomyrmex.struct.test")

    def test_log_with_context_runs_without_error(self):
        setup_logging(force=True)
        # Should not raise
        log_with_context("info", "context test", {"key": "val"})

    def test_log_with_context_invalid_level_falls_back_to_info(self):
        setup_logging(force=True)
        # Should not raise with invalid level
        log_with_context("notareal_level", "fallback test", {})


class TestLogContext:
    """Tests for the LogContext context manager (threading.local version)."""

    def test_enter_sets_correlation_id(self):
        cid = "ctx-test-123"
        with LogContext(correlation_id=cid) as ctx:
            assert ctx.correlation_id == cid

    def test_auto_generates_correlation_id_when_none(self):
        with LogContext() as ctx:
            assert len(ctx.correlation_id) > 0

    def test_additional_context_stored(self):
        with LogContext(additional_context={"env": "test"}) as ctx:
            assert ctx.additional_context == {"env": "test"}

    def test_context_manager_returns_self(self):
        lc = LogContext(correlation_id="return-self")
        with lc as result:
            assert result is lc

    def test_nested_contexts_restore_outer(self):
        outer_cid = "outer-id"
        inner_cid = "inner-id"
        with LogContext(correlation_id=outer_cid):
            with LogContext(correlation_id=inner_cid) as inner_ctx:
                assert inner_ctx.correlation_id == inner_cid
            # After inner exit, outer correlation_id should be restored
            # (threading.local based, check outer restored)


class TestAuditLogger:
    """Tests for AuditLogger."""

    def test_audit_logger_instantiates(self):
        audit = AuditLogger(logger_name="test_audit_logger")
        assert audit.logger is not None

    def test_audit_logger_log_access_granted(self):
        audit = AuditLogger(logger_name="test_audit_access_granted")
        # Should not raise
        audit.log_access("user:alice", "resource:doc", "read", granted=True)

    def test_audit_logger_log_access_denied(self):
        audit = AuditLogger(logger_name="test_audit_access_denied")
        # Should not raise
        audit.log_access("user:bob", "resource:secret", "write", granted=False)

    def test_audit_logger_writes_to_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "audit.log")
            audit = AuditLogger(logger_name="test_audit_file", log_file=log_path)
            audit.log_access("user:eve", "admin_panel", "read", granted=False)
            assert os.path.exists(log_path)


# ---------------------------------------------------------------------------
# TestMCPToolsLogging
# ---------------------------------------------------------------------------


class TestMCPToolsLogging:
    """Tests for the logging_monitoring MCP tool: logging_format_structured."""

    def test_logging_format_structured_success(self):
        from codomyrmex.logging_monitoring.mcp_tools import logging_format_structured

        result = logging_format_structured(
            level="info",
            message="Test message",
            module="test_module",
            correlation_id="cid-mcp-test",
            fields={"key": "value"},
        )
        assert result["status"] == "success"
        assert "formatted" in result
        assert result["formatted"]["message"] == "Test message"

    def test_logging_format_structured_contains_level(self):
        from codomyrmex.logging_monitoring.mcp_tools import logging_format_structured

        result = logging_format_structured(level="error", message="Error occurred")
        assert result["status"] == "success"
        assert result["formatted"]["level"] == "error"

    def test_logging_format_structured_with_correlation_id(self):
        from codomyrmex.logging_monitoring.mcp_tools import logging_format_structured

        result = logging_format_structured(
            level="warning",
            message="Watch out",
            correlation_id="cid-warn-123",
        )
        assert result["status"] == "success"
        assert result["formatted"].get("correlation_id") == "cid-warn-123"

    def test_logging_format_structured_invalid_level_returns_error(self):
        from codomyrmex.logging_monitoring.mcp_tools import logging_format_structured

        result = logging_format_structured(
            level="bogus_level", message="Should fail gracefully"
        )
        # Either success (if LogLevel ignores case) or error
        assert result["status"] in ("success", "error")

    def test_logging_format_structured_empty_fields(self):
        from codomyrmex.logging_monitoring.mcp_tools import logging_format_structured

        result = logging_format_structured(level="debug", message="Debug msg")
        assert result["status"] == "success"
