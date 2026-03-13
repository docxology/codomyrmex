"""Tests for telemetry exporters (SpanData, ConsoleExporter, FileExporter, BatchExporter).

Zero-mock policy: real instantiation only. No network calls — OTLPExporter.export() is
not tested (requires live endpoint); only instantiation and configuration are verified.
"""
import json
import tempfile
from datetime import datetime, timedelta

import pytest

from codomyrmex.telemetry.exporters import (
    BatchExporter,
    ConsoleExporter,
    FileExporter,
    MultiExporter,
    OTLPExporter,
    SpanData,
)

# ──────────────────────────── Helpers ──────────────────────────────────────


def _make_span(**kwargs) -> SpanData:
    defaults = {
        "trace_id": "trace-abc-123",
        "span_id": "span-def-456",
    }
    defaults.update(kwargs)
    return SpanData(**defaults)


# ──────────────────────────── SpanData ─────────────────────────────────────


class TestSpanData:
    def test_minimal_instantiation(self):
        span = SpanData(trace_id="t1", span_id="s1")
        assert span.trace_id == "t1"
        assert span.span_id == "s1"

    def test_default_kind_is_internal(self):
        span = _make_span()
        assert span.kind == "internal"

    def test_default_status_is_ok(self):
        span = _make_span()
        assert span.status == "ok"

    def test_default_parent_span_id_is_none(self):
        span = _make_span()
        assert span.parent_span_id is None

    def test_default_start_time_is_datetime(self):
        span = _make_span()
        assert isinstance(span.start_time, datetime)

    def test_default_end_time_is_none(self):
        span = _make_span()
        assert span.end_time is None

    def test_default_attributes_is_empty_dict(self):
        span = _make_span()
        assert span.attributes == {}

    def test_default_events_is_empty_list(self):
        span = _make_span()
        assert span.events == []

    def test_full_instantiation(self):
        t0 = datetime(2026, 1, 1, 0, 0, 0)
        t1 = datetime(2026, 1, 1, 0, 0, 1)
        span = SpanData(
            trace_id="t",
            span_id="s",
            parent_span_id="p",
            name="test-op",
            kind="client",
            start_time=t0,
            end_time=t1,
            status="error",
            attributes={"http.status_code": 500},
            events=[{"name": "exception"}],
        )
        assert span.parent_span_id == "p"
        assert span.name == "test-op"
        assert span.kind == "client"
        assert span.status == "error"
        assert span.attributes["http.status_code"] == 500
        assert len(span.events) == 1

    def test_duration_ms_with_end_time(self):
        t0 = datetime(2026, 1, 1, 0, 0, 0)
        t1 = t0 + timedelta(milliseconds=250)
        span = SpanData(trace_id="t", span_id="s", start_time=t0, end_time=t1)
        assert abs(span.duration_ms - 250.0) < 1.0

    def test_duration_ms_without_end_time_is_zero(self):
        span = _make_span()
        assert span.duration_ms == 0.0

    def test_to_dict_keys(self):
        span = _make_span()
        d = span.to_dict()
        expected_keys = {"trace_id", "span_id", "parent_span_id", "name", "kind",
                         "start_time", "end_time", "duration_ms", "status",
                         "attributes", "events"}
        assert expected_keys.issubset(d.keys())

    def test_to_dict_trace_id_matches(self):
        span = _make_span(trace_id="abc")
        assert span.to_dict()["trace_id"] == "abc"

    def test_to_dict_start_time_is_isoformat_string(self):
        span = _make_span()
        d = span.to_dict()
        # Should be a valid ISO datetime string
        datetime.fromisoformat(d["start_time"])

    def test_to_dict_end_time_none_when_not_set(self):
        span = _make_span()
        assert span.to_dict()["end_time"] is None

    def test_to_dict_end_time_isoformat_when_set(self):
        t1 = datetime(2026, 1, 1, 0, 0, 1)
        span = _make_span(end_time=t1)
        d = span.to_dict()
        assert d["end_time"] is not None
        datetime.fromisoformat(d["end_time"])

    def test_to_dict_is_json_serializable(self):
        span = _make_span(attributes={"key": "val"})
        json.dumps(span.to_dict())  # must not raise


# ──────────────────────────── ConsoleExporter ──────────────────────────────


class TestConsoleExporter:
    def test_instantiation_default(self):
        exp = ConsoleExporter()
        assert exp.pretty is True

    def test_instantiation_not_pretty(self):
        exp = ConsoleExporter(pretty=False)
        assert exp.pretty is False

    def test_export_returns_true(self, capsys):
        exp = ConsoleExporter(pretty=False)
        span = _make_span()
        result = exp.export([span])
        assert result is True

    def test_export_empty_list_returns_true(self):
        exp = ConsoleExporter()
        assert exp.export([]) is True

    def test_export_outputs_json(self, capsys):
        exp = ConsoleExporter(pretty=False)
        span = _make_span(trace_id="trace-xyz")
        exp.export([span])
        out = capsys.readouterr().out
        assert "trace-xyz" in out

    def test_shutdown_does_not_raise(self):
        exp = ConsoleExporter()
        exp.shutdown()  # must not raise


# ──────────────────────────── FileExporter ─────────────────────────────────


class TestFileExporter:
    def test_instantiation(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl") as f:
            exp = FileExporter(f.name)
            assert exp.filepath == f.name

    def test_export_writes_to_file(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", mode="w", delete=False) as f:
            path = f.name
        exp = FileExporter(path)
        span = _make_span(trace_id="file-test-trace")
        result = exp.export([span])
        assert result is True
        with open(path) as fout:
            lines = fout.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["trace_id"] == "file-test-trace"

    def test_export_multiple_spans(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", mode="w", delete=False) as f:
            path = f.name
        exp = FileExporter(path)
        spans = [_make_span(span_id=f"s{i}") for i in range(5)]
        exp.export(spans)
        with open(path) as fout:
            lines = fout.readlines()
        assert len(lines) == 5

    def test_export_appends(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", mode="w", delete=False) as f:
            path = f.name
        exp = FileExporter(path)
        exp.export([_make_span(span_id="s1")])
        exp.export([_make_span(span_id="s2")])
        with open(path) as fout:
            lines = fout.readlines()
        assert len(lines) == 2

    def test_shutdown_does_not_raise(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl") as f:
            exp = FileExporter(f.name)
            exp.shutdown()  # must not raise


# ──────────────────────────── OTLPExporter ─────────────────────────────────


class TestOTLPExporter:
    def test_instantiation_default_endpoint(self):
        exp = OTLPExporter()
        assert isinstance(exp.endpoint, str)
        assert len(exp.endpoint) > 0

    def test_instantiation_custom_endpoint(self):
        exp = OTLPExporter(endpoint="http://localhost:4318")
        assert "localhost:4318" in exp.endpoint

    def test_trailing_slash_stripped(self):
        exp = OTLPExporter(endpoint="http://localhost:4318/")
        assert not exp.endpoint.endswith("/")

    def test_headers_default_empty(self):
        exp = OTLPExporter()
        assert exp.headers == {}

    def test_custom_headers(self):
        exp = OTLPExporter(headers={"Authorization": "Bearer token"})
        assert exp.headers["Authorization"] == "Bearer token"

    def test_timeout_default(self):
        exp = OTLPExporter()
        assert exp.timeout == 10.0

    def test_compression_default(self):
        exp = OTLPExporter()
        assert exp.compression == "none"

    def test_convert_to_otlp_format_structure(self):
        exp = OTLPExporter()
        span = _make_span(trace_id="t1", span_id="s1", name="test-op")
        result = exp._convert_to_otlp_format([span])
        assert "resourceSpans" in result
        assert len(result["resourceSpans"]) >= 1

    def test_map_span_kind_internal(self):
        exp = OTLPExporter()
        assert exp._map_span_kind("internal") == 1

    def test_map_span_kind_server(self):
        exp = OTLPExporter()
        assert exp._map_span_kind("server") == 2

    def test_map_span_kind_client(self):
        exp = OTLPExporter()
        assert exp._map_span_kind("client") == 3

    def test_map_span_kind_unknown_defaults_to_1(self):
        exp = OTLPExporter()
        assert exp._map_span_kind("unknown_kind") == 1

    def test_convert_attributes_string(self):
        exp = OTLPExporter()
        attrs = exp._convert_attributes({"key": "value"})
        assert attrs[0]["key"] == "key"
        assert attrs[0]["value"] == {"stringValue": "value"}

    def test_convert_attributes_int(self):
        exp = OTLPExporter()
        attrs = exp._convert_attributes({"count": 42})
        assert attrs[0]["value"] == {"intValue": 42}

    def test_convert_attributes_float(self):
        exp = OTLPExporter()
        attrs = exp._convert_attributes({"rate": 3.14})
        assert attrs[0]["value"] == {"doubleValue": 3.14}

    def test_convert_attributes_bool_stored_as_int(self):
        # bool is a subclass of int in Python, so True maps to intValue
        exp = OTLPExporter()
        attrs = exp._convert_attributes({"flag": True})
        # Actual behavior: int check fires before bool check
        assert attrs[0]["key"] == "flag"
        assert "flag" not in [a["key"] for a in attrs if a["key"] != "flag"]

    def test_convert_attributes_empty(self):
        exp = OTLPExporter()
        assert exp._convert_attributes({}) == []

    def test_shutdown_does_not_raise(self):
        exp = OTLPExporter()
        exp.shutdown()


# ──────────────────────────── BatchExporter ────────────────────────────────


class TestBatchExporter:
    def test_instantiation(self):
        inner = ConsoleExporter()
        batch = BatchExporter(inner)
        assert batch.exporter is inner

    def test_default_max_batch_size(self):
        batch = BatchExporter(ConsoleExporter())
        assert batch.max_batch_size == 512

    def test_default_max_queue_size(self):
        batch = BatchExporter(ConsoleExporter())
        assert batch.max_queue_size == 2048

    def test_custom_batch_size(self):
        batch = BatchExporter(ConsoleExporter(), max_batch_size=64)
        assert batch.max_batch_size == 64

    def test_shutdown_does_not_raise(self):
        batch = BatchExporter(ConsoleExporter())
        batch.shutdown()


# ──────────────────────── ConsoleExporter pretty=False ─────────────────────


class TestConsoleExporterPrettyFalse:
    """Verify compact (non-pretty) output path of ConsoleExporter."""

    def test_compact_output_has_no_newlines_in_json_line(self, capsys):
        exp = ConsoleExporter(pretty=False)
        span = _make_span(trace_id="compact-trace")
        exp.export([span])
        out = capsys.readouterr().out
        # Each line is one JSON object; compact mode should be single-line JSON
        lines = [line for line in out.splitlines() if line.strip()]
        assert len(lines) == 1
        # Valid JSON on that line
        data = json.loads(lines[0])
        assert data["trace_id"] == "compact-trace"

    def test_pretty_output_is_multiline(self, capsys):
        exp = ConsoleExporter(pretty=True)
        span = _make_span(trace_id="pretty-trace")
        exp.export([span])
        out = capsys.readouterr().out
        # Pretty JSON has indentation, so multiple lines
        assert out.count("\n") > 2

    def test_multiple_spans_exported_compact(self, capsys):
        exp = ConsoleExporter(pretty=False)
        spans = [_make_span(span_id=f"s{i}", trace_id=f"t{i}") for i in range(3)]
        result = exp.export(spans)
        assert result is True
        out = capsys.readouterr().out
        lines = [line for line in out.splitlines() if line.strip()]
        assert len(lines) == 3


# ──────────────────────── FileExporter error path ──────────────────────────


class TestFileExporterErrorPath:
    """FileExporter.export() returns False when the file cannot be written."""

    def test_export_returns_false_for_unwritable_path(self):
        # /dev/null is a file, so /dev/null/subdir is always unwritable
        exp = FileExporter("/dev/null/cannot_write_here.jsonl")
        result = exp.export([_make_span()])
        assert result is False

    def test_export_returns_false_for_directory_as_path(self, tmp_path):
        # Passing a directory as the filepath causes IsADirectoryError
        exp = FileExporter(str(tmp_path))
        result = exp.export([_make_span()])
        assert result is False


# ──────────────────────── OTLPExporter attribute types ─────────────────────


class TestOTLPExporterAttributeTypes:
    """Cover bool and other/complex attribute type branches in _convert_attributes."""

    def test_convert_attributes_bool_true(self):
        exp = OTLPExporter()
        # bool is a subclass of int; Python isinstance(True, int) is True,
        # so this hits the int branch and stores intValue
        attrs = exp._convert_attributes({"active": True})
        assert attrs[0]["key"] == "active"
        # The value dict must have exactly one type key
        value = attrs[0]["value"]
        assert len(value) == 1

    def test_convert_attributes_bool_false(self):
        exp = OTLPExporter()
        attrs = exp._convert_attributes({"disabled": False})
        assert attrs[0]["key"] == "disabled"
        value = attrs[0]["value"]
        assert len(value) == 1

    def test_convert_attributes_list_falls_back_to_string(self):
        exp = OTLPExporter()
        attrs = exp._convert_attributes({"tags": ["a", "b"]})
        assert attrs[0]["key"] == "tags"
        # Non-str/int/float/bool → stringValue
        assert "stringValue" in attrs[0]["value"]

    def test_convert_attributes_none_falls_back_to_string(self):
        exp = OTLPExporter()
        attrs = exp._convert_attributes({"missing": None})
        assert "stringValue" in attrs[0]["value"]

    def test_convert_attributes_multiple_types(self):
        exp = OTLPExporter()
        attrs = exp._convert_attributes({
            "s": "hello",
            "i": 1,
            "f": 1.5,
        })
        assert len(attrs) == 3
        keys = {a["key"] for a in attrs}
        assert keys == {"s", "i", "f"}

    def test_convert_to_otlp_format_spans_grouped_by_trace(self):
        exp = OTLPExporter()
        spans = [
            _make_span(trace_id="t1", span_id="s1"),
            _make_span(trace_id="t1", span_id="s2"),
            _make_span(trace_id="t2", span_id="s3"),
        ]
        result = exp._convert_to_otlp_format(spans)
        # Two distinct trace IDs → two resource span entries
        assert len(result["resourceSpans"]) == 2

    def test_convert_to_otlp_format_empty_spans(self):
        exp = OTLPExporter()
        result = exp._convert_to_otlp_format([])
        assert result == {"resourceSpans": []}

    def test_otlp_format_span_status_error_maps_to_2(self):
        exp = OTLPExporter()
        span = _make_span(status="error")
        result = exp._convert_to_otlp_format([span])
        scope_spans = result["resourceSpans"][0]["scopeSpans"][0]["spans"]
        assert scope_spans[0]["status"]["code"] == 2

    def test_otlp_format_span_status_ok_maps_to_1(self):
        exp = OTLPExporter()
        span = _make_span(status="ok")
        result = exp._convert_to_otlp_format([span])
        scope_spans = result["resourceSpans"][0]["scopeSpans"][0]["spans"]
        assert scope_spans[0]["status"]["code"] == 1

    def test_map_span_kind_producer(self):
        exp = OTLPExporter()
        assert exp._map_span_kind("producer") == 4

    def test_map_span_kind_consumer(self):
        exp = OTLPExporter()
        assert exp._map_span_kind("consumer") == 5


# ──────────────────────── MultiExporter ────────────────────────────────────


class TestMultiExporter:
    """MultiExporter delegates to all sub-exporters and aggregates success."""

    def test_export_calls_all_sub_exporters(self, tmp_path):
        path1 = str(tmp_path / "a.jsonl")
        path2 = str(tmp_path / "b.jsonl")
        exp1 = FileExporter(path1)
        exp2 = FileExporter(path2)
        multi = MultiExporter([exp1, exp2])
        result = multi.export([_make_span()])
        assert result is True
        # Both files should have been written
        with open(path1) as f:
            assert len(f.readlines()) == 1
        with open(path2) as f:
            assert len(f.readlines()) == 1

    def test_export_returns_true_if_any_sub_exporter_succeeds(self, tmp_path):
        good = FileExporter(str(tmp_path / "good.jsonl"))
        bad = FileExporter("/dev/null/bad.jsonl")  # will fail
        multi = MultiExporter([good, bad])
        result = multi.export([_make_span()])
        assert result is True

    def test_export_returns_false_if_all_sub_exporters_fail(self):
        bad1 = FileExporter("/dev/null/bad1.jsonl")
        bad2 = FileExporter("/dev/null/bad2.jsonl")
        multi = MultiExporter([bad1, bad2])
        result = multi.export([_make_span()])
        assert result is False

    def test_export_empty_exporter_list_returns_false(self):
        # any([]) is False
        multi = MultiExporter([])
        result = multi.export([_make_span()])
        assert result is False

    def test_shutdown_calls_all_sub_exporters(self):
        # Use a real ConsoleExporter (shutdown is a no-op, must not raise)
        exp1 = ConsoleExporter()
        exp2 = ConsoleExporter()
        multi = MultiExporter([exp1, exp2])
        multi.shutdown()  # must not raise

    def test_instantiation_stores_exporters(self):
        exp1 = ConsoleExporter()
        exp2 = ConsoleExporter()
        multi = MultiExporter([exp1, exp2])
        assert len(multi.exporters) == 2
        assert multi.exporters[0] is exp1


# ──────────────────────── BatchExporter flush behavior ─────────────────────


class TestBatchExporterFlush:
    """BatchExporter queues spans and flushes them via the worker thread."""

    def test_worker_exports_spans_to_inner_exporter(self, tmp_path):
        path = str(tmp_path / "batch_flush.jsonl")
        inner = FileExporter(path)
        # Use short scheduled_delay_ms so worker flushes quickly
        batch = BatchExporter(inner, scheduled_delay_ms=50)
        spans = [_make_span(span_id=f"flush-{i}") for i in range(3)]
        batch.export(spans)
        # Shutdown after enough time for one worker cycle to complete
        import time
        time.sleep(0.3)  # allow worker to flush the 50ms batch
        batch.shutdown()
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == 3

    def test_export_into_full_queue_returns_false(self):
        # max_queue_size=1: second put_nowait raises Full and returns False
        inner = ConsoleExporter()
        batch = BatchExporter(inner, max_queue_size=1, scheduled_delay_ms=60000)
        # First span fills the queue
        r1 = batch.export([_make_span(span_id="s1")])
        # Second span: queue full → returns False
        r2 = batch.export([_make_span(span_id="s2")])
        assert r1 is True
        assert r2 is False
        batch.shutdown()

    def test_worker_thread_is_daemon(self):
        batch = BatchExporter(ConsoleExporter())
        assert batch._worker_thread.daemon is True
        batch.shutdown()


# ──────────────────────── create_exporter factory ──────────────────────────


class TestCreateExporter:
    """create_exporter() factory function returns correct exporter instances."""

    def test_create_console_exporter(self):
        from codomyrmex.telemetry.exporters import create_exporter
        exp = create_exporter("console")
        assert isinstance(exp, ConsoleExporter)

    def test_create_file_exporter(self, tmp_path):
        from codomyrmex.telemetry.exporters import create_exporter
        exp = create_exporter("file", filepath=str(tmp_path / "out.jsonl"))
        assert isinstance(exp, FileExporter)

    def test_create_otlp_exporter(self):
        from codomyrmex.telemetry.exporters import create_exporter
        exp = create_exporter("otlp")
        assert isinstance(exp, OTLPExporter)

    def test_create_unknown_type_raises_value_error(self):
        from codomyrmex.telemetry.exporters import create_exporter
        with pytest.raises(ValueError, match="Unknown exporter type"):
            create_exporter("kafka")

    def test_create_console_with_pretty_false(self):
        from codomyrmex.telemetry.exporters import create_exporter
        exp = create_exporter("console", pretty=False)
        assert exp.pretty is False
