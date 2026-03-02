"""
Unit tests for logging_monitoring.formatters.structured_formatter — Zero-Mock compliant.

Covers: LogLevel, LogContext, FormatterConfig, StructuredLogEntry, StructuredFormatter
"""

import json

import pytest

from codomyrmex.logging_monitoring.formatters.structured_formatter import (
    FormatterConfig,
    LogContext,
    LogLevel,
    StructuredFormatter,
    StructuredLogEntry,
)


def _entry(
    level=LogLevel.INFO,
    message="test",
    correlation_id="",
    module="",
    **fields,
):
    ctx = LogContext(correlation_id=correlation_id, module=module)
    return StructuredLogEntry(level=level, message=message, context=ctx, fields=fields)


# ── Enum + Dataclass ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestLogLevel:
    def test_values(self):
        assert LogLevel.DEBUG.value == "debug"
        assert LogLevel.INFO.value == "info"
        assert LogLevel.WARNING.value == "warning"
        assert LogLevel.ERROR.value == "error"
        assert LogLevel.CRITICAL.value == "critical"


@pytest.mark.unit
class TestLogContext:
    def test_defaults(self):
        ctx = LogContext()
        assert ctx.correlation_id == ""
        assert ctx.module == ""
        assert ctx.function == ""
        assert ctx.extra == {}

    def test_explicit_values(self):
        ctx = LogContext(correlation_id="cid-1", module="api", function="handler")
        assert ctx.correlation_id == "cid-1"
        assert ctx.function == "handler"


@pytest.mark.unit
class TestFormatterConfig:
    def test_defaults(self):
        cfg = FormatterConfig()
        assert cfg.include_timestamp is True
        assert cfg.include_level is True
        assert cfg.pretty_print is False
        assert cfg.max_message_length == 0
        assert cfg.timestamp_key == "timestamp"
        assert cfg.message_key == "message"


# ── StructuredFormatter ────────────────────────────────────────────────────


@pytest.mark.unit
class TestStructuredFormatterBasic:
    def test_format_returns_string(self):
        fmt = StructuredFormatter()
        result = fmt.format(_entry())
        assert isinstance(result, str)

    def test_format_is_valid_json(self):
        fmt = StructuredFormatter()
        parsed = json.loads(fmt.format(_entry()))
        assert isinstance(parsed, dict)

    def test_format_contains_message(self):
        fmt = StructuredFormatter()
        parsed = json.loads(fmt.format(_entry(message="hello")))
        assert parsed["message"] == "hello"

    def test_format_contains_level(self):
        fmt = StructuredFormatter()
        parsed = json.loads(fmt.format(_entry(level=LogLevel.WARNING)))
        assert parsed["level"] == "warning"

    def test_format_contains_timestamp(self):
        fmt = StructuredFormatter()
        parsed = json.loads(fmt.format(_entry()))
        assert "timestamp" in parsed

    def test_lines_formatted_increments(self):
        fmt = StructuredFormatter()
        assert fmt.lines_formatted == 0
        fmt.format(_entry())
        fmt.format(_entry())
        assert fmt.lines_formatted == 2

    def test_reset_count(self):
        fmt = StructuredFormatter()
        fmt.format(_entry())
        fmt.reset_count()
        assert fmt.lines_formatted == 0


@pytest.mark.unit
class TestStructuredFormatterConfig:
    def test_custom_timestamp_key(self):
        fmt = StructuredFormatter(config=FormatterConfig(timestamp_key="ts"))
        parsed = json.loads(fmt.format(_entry()))
        assert "ts" in parsed
        assert "timestamp" not in parsed

    def test_custom_level_key(self):
        fmt = StructuredFormatter(config=FormatterConfig(level_key="severity"))
        parsed = json.loads(fmt.format(_entry()))
        assert "severity" in parsed

    def test_custom_message_key(self):
        fmt = StructuredFormatter(config=FormatterConfig(message_key="msg"))
        parsed = json.loads(fmt.format(_entry(message="hello")))
        assert parsed["msg"] == "hello"

    def test_no_timestamp_when_disabled(self):
        fmt = StructuredFormatter(config=FormatterConfig(include_timestamp=False))
        parsed = json.loads(fmt.format(_entry()))
        assert "timestamp" not in parsed

    def test_no_level_when_disabled(self):
        fmt = StructuredFormatter(config=FormatterConfig(include_level=False))
        parsed = json.loads(fmt.format(_entry()))
        assert "level" not in parsed

    def test_pretty_print_produces_indented_json(self):
        fmt = StructuredFormatter(config=FormatterConfig(pretty_print=True))
        result = fmt.format(_entry())
        assert "\n" in result

    def test_static_fields_included(self):
        fmt = StructuredFormatter(
            config=FormatterConfig(static_fields={"service": "api", "env": "test"})
        )
        parsed = json.loads(fmt.format(_entry()))
        assert parsed["service"] == "api"
        assert parsed["env"] == "test"

    def test_message_truncation(self):
        fmt = StructuredFormatter(config=FormatterConfig(max_message_length=10))
        parsed = json.loads(fmt.format(_entry(message="x" * 20)))
        assert len(parsed["message"]) == 13  # 10 + "..."
        assert parsed["message"].endswith("...")

    def test_message_not_truncated_when_short(self):
        fmt = StructuredFormatter(config=FormatterConfig(max_message_length=100))
        parsed = json.loads(fmt.format(_entry(message="short")))
        assert parsed["message"] == "short"

    def test_no_truncation_when_limit_zero(self):
        fmt = StructuredFormatter(config=FormatterConfig(max_message_length=0))
        long_msg = "x" * 500
        parsed = json.loads(fmt.format(_entry(message=long_msg)))
        assert parsed["message"] == long_msg


@pytest.mark.unit
class TestStructuredFormatterContext:
    def test_correlation_id_included(self):
        fmt = StructuredFormatter()
        parsed = json.loads(fmt.format(_entry(correlation_id="cid-abc")))
        assert parsed["correlation_id"] == "cid-abc"

    def test_correlation_id_omitted_when_empty(self):
        fmt = StructuredFormatter()
        parsed = json.loads(fmt.format(_entry()))
        assert "correlation_id" not in parsed

    def test_module_included(self):
        fmt = StructuredFormatter()
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            message="test",
            context=LogContext(module="mymod", function="myfn"),
        )
        parsed = json.loads(fmt.format(entry))
        assert parsed["module"] == "mymod"
        assert parsed["function"] == "myfn"

    def test_module_omitted_when_not_set(self):
        fmt = StructuredFormatter(config=FormatterConfig(include_module=True))
        parsed = json.loads(fmt.format(_entry()))
        # No module in context → field not added
        assert "module" not in parsed

    def test_extra_context_included(self):
        fmt = StructuredFormatter()
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            message="test",
            context=LogContext(extra={"request_id": "req-1"}),
        )
        parsed = json.loads(fmt.format(entry))
        assert parsed["context"]["request_id"] == "req-1"

    def test_entry_fields_included(self):
        fmt = StructuredFormatter()
        entry = _entry(message="test", **{"duration_ms": 42})
        parsed = json.loads(fmt.format(entry))
        assert parsed["duration_ms"] == 42


@pytest.mark.unit
class TestStructuredFormatterErrors:
    def test_error_fields_on_error_level(self):
        fmt = StructuredFormatter()
        err = ValueError("something went wrong")
        entry = StructuredLogEntry(
            level=LogLevel.ERROR,
            message="failure",
            error=err,
        )
        parsed = json.loads(fmt.format(entry))
        assert parsed["error_type"] == "ValueError"
        assert "something went wrong" in parsed["error_message"]
        assert "stacktrace" in parsed

    def test_no_stacktrace_on_info_level(self):
        fmt = StructuredFormatter()
        err = ValueError("not critical")
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            message="info",
            error=err,
        )
        parsed = json.loads(fmt.format(entry))
        assert "stacktrace" not in parsed

    def test_no_stacktrace_when_disabled(self):
        fmt = StructuredFormatter(config=FormatterConfig(include_stacktrace=False))
        err = ValueError("error")
        entry = StructuredLogEntry(
            level=LogLevel.ERROR,
            message="error msg",
            error=err,
        )
        parsed = json.loads(fmt.format(entry))
        assert "stacktrace" not in parsed


@pytest.mark.unit
class TestStructuredFormatterBatch:
    def test_format_batch_returns_string(self):
        fmt = StructuredFormatter()
        result = fmt.format_batch([_entry(message="a"), _entry(message="b")])
        assert isinstance(result, str)

    def test_format_batch_newline_separated(self):
        fmt = StructuredFormatter()
        result = fmt.format_batch([_entry(message="a"), _entry(message="b")])
        lines = result.split("\n")
        assert len(lines) == 2

    def test_format_batch_each_line_is_valid_json(self):
        fmt = StructuredFormatter()
        result = fmt.format_batch([_entry(message="x"), _entry(message="y")])
        for line in result.split("\n"):
            parsed = json.loads(line)
            assert "message" in parsed

    def test_format_batch_empty_returns_empty(self):
        fmt = StructuredFormatter()
        result = fmt.format_batch([])
        assert result == ""
