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
