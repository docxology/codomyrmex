"""Zero-mock tests for telemetry.tracing.models — SpanKind, SpanStatus, SpanContext,
and Span with all methods, properties, and chaining API."""

import time

import pytest

from codomyrmex.telemetry.tracing.models import (
    Span,
    SpanContext,
    SpanKind,
    SpanStatus,
)

# ──────────────────────────── Helpers ─────────────────────────────────────


def _make_context(
    trace_id: str = "trace-abc",
    span_id: str = "span-xyz",
    parent_span_id: str | None = None,
) -> SpanContext:
    return SpanContext(
        trace_id=trace_id, span_id=span_id, parent_span_id=parent_span_id
    )


def _make_span(name: str = "test-op", **kwargs) -> Span:
    ctx = _make_context()
    return Span(name=name, context=ctx, **kwargs)


# ──────────────────────────── SpanKind ────────────────────────────────────


@pytest.mark.unit
class TestSpanKind:
    """Tests for SpanKind enum."""

    def test_all_five_members(self):
        names = {m.name for m in SpanKind}
        assert names == {"INTERNAL", "SERVER", "CLIENT", "PRODUCER", "CONSUMER"}

    def test_values_are_lowercase(self):
        for member in SpanKind:
            assert member.value == member.value.lower()

    def test_lookup_by_value(self):
        assert SpanKind("server") is SpanKind.SERVER
        assert SpanKind("consumer") is SpanKind.CONSUMER

    def test_internal_is_default_kind(self):
        span = _make_span()
        assert span.kind is SpanKind.INTERNAL


# ──────────────────────────── SpanStatus ──────────────────────────────────


@pytest.mark.unit
class TestSpanStatus:
    """Tests for SpanStatus enum."""

    def test_exactly_three_members(self):
        assert len(list(SpanStatus)) == 3

    def test_member_names(self):
        names = {m.name for m in SpanStatus}
        assert names == {"UNSET", "OK", "ERROR"}

    def test_lookup_by_value(self):
        assert SpanStatus("ok") is SpanStatus.OK
        assert SpanStatus("error") is SpanStatus.ERROR

    def test_unset_is_default_status(self):
        span = _make_span()
        assert span.status is SpanStatus.UNSET


# ──────────────────────────── SpanContext ─────────────────────────────────


@pytest.mark.unit
class TestSpanContext:
    """Tests for SpanContext dataclass."""

    def test_construction_required_fields(self):
        ctx = SpanContext(trace_id="t1", span_id="s1")
        assert ctx.trace_id == "t1"
        assert ctx.span_id == "s1"

    def test_parent_span_id_defaults_none(self):
        ctx = SpanContext(trace_id="t", span_id="s")
        assert ctx.parent_span_id is None

    def test_sampled_defaults_true(self):
        ctx = SpanContext(trace_id="t", span_id="s")
        assert ctx.sampled is True

    def test_baggage_defaults_empty(self):
        ctx = SpanContext(trace_id="t", span_id="s")
        assert ctx.baggage == {}

    def test_to_dict_has_all_keys(self):
        ctx = _make_context()
        d = ctx.to_dict()
        assert set(d.keys()) == {
            "trace_id",
            "span_id",
            "parent_span_id",
            "sampled",
            "baggage",
        }

    def test_to_dict_values_match(self):
        ctx = SpanContext(
            trace_id="t-99",
            span_id="s-88",
            parent_span_id="p-77",
            sampled=False,
            baggage={"env": "prod"},
        )
        d = ctx.to_dict()
        assert d["trace_id"] == "t-99"
        assert d["span_id"] == "s-88"
        assert d["parent_span_id"] == "p-77"
        assert d["sampled"] is False
        assert d["baggage"] == {"env": "prod"}

    def test_from_dict_round_trip(self):
        ctx = SpanContext(
            trace_id="tid",
            span_id="sid",
            parent_span_id="pid",
            sampled=True,
            baggage={"user": "alice"},
        )
        restored = SpanContext.from_dict(ctx.to_dict())
        assert restored.trace_id == ctx.trace_id
        assert restored.span_id == ctx.span_id
        assert restored.parent_span_id == ctx.parent_span_id
        assert restored.sampled == ctx.sampled
        assert restored.baggage == ctx.baggage

    def test_from_dict_optional_parent_absent(self):
        data = {"trace_id": "t", "span_id": "s"}
        ctx = SpanContext.from_dict(data)
        assert ctx.parent_span_id is None
        assert ctx.sampled is True
        assert ctx.baggage == {}

    def test_to_headers_produces_correct_keys(self):
        ctx = _make_context(trace_id="abc", span_id="def")
        headers = ctx.to_headers()
        assert headers["X-Trace-Id"] == "abc"
        assert headers["X-Span-Id"] == "def"
        assert "X-Sampled" in headers

    def test_to_headers_sampled_lowercase_true(self):
        ctx = SpanContext(trace_id="t", span_id="s", sampled=True)
        headers = ctx.to_headers()
        assert headers["X-Sampled"] == "true"

    def test_to_headers_sampled_lowercase_false(self):
        ctx = SpanContext(trace_id="t", span_id="s", sampled=False)
        headers = ctx.to_headers()
        assert headers["X-Sampled"] == "false"

    def test_to_headers_parent_empty_string_when_none(self):
        ctx = SpanContext(trace_id="t", span_id="s", parent_span_id=None)
        headers = ctx.to_headers()
        assert headers["X-Parent-Span-Id"] == ""

    def test_from_headers_extracts_trace_and_span(self):
        headers = {"X-Trace-Id": "trace-1", "X-Span-Id": "span-2"}
        ctx = SpanContext.from_headers(headers)
        assert ctx is not None
        assert ctx.trace_id == "trace-1"
        assert ctx.span_id == "span-2"

    def test_from_headers_returns_none_when_missing_trace(self):
        headers = {"X-Span-Id": "s"}
        ctx = SpanContext.from_headers(headers)
        assert ctx is None

    def test_from_headers_returns_none_when_missing_span(self):
        headers = {"X-Trace-Id": "t"}
        ctx = SpanContext.from_headers(headers)
        assert ctx is None

    def test_from_headers_returns_none_empty_dict(self):
        ctx = SpanContext.from_headers({})
        assert ctx is None

    def test_from_headers_lowercase_keys(self):
        headers = {"x-trace-id": "t-lower", "x-span-id": "s-lower"}
        ctx = SpanContext.from_headers(headers)
        assert ctx is not None
        assert ctx.trace_id == "t-lower"


# ──────────────────────────── Span ────────────────────────────────────────


@pytest.mark.unit
class TestSpan:
    """Tests for Span dataclass and its methods."""

    def test_delegation_trace_id(self):
        span = _make_span()
        assert span.trace_id == span.context.trace_id

    def test_delegation_span_id(self):
        span = _make_span()
        assert span.span_id == span.context.span_id

    def test_delegation_parent_span_id_none(self):
        span = _make_span()
        assert span.parent_span_id is None

    def test_delegation_parent_span_id_set(self):
        ctx = _make_context(parent_span_id="parent-111")
        span = Span(name="child", context=ctx)
        assert span.parent_span_id == "parent-111"

    def test_duration_ms_positive_before_finish(self):
        span = _make_span()
        duration = span.duration_ms
        assert duration >= 0

    def test_duration_ms_after_finish(self):
        span = _make_span()
        time.sleep(0.01)
        span.finish()
        duration = span.duration_ms
        assert duration >= 10.0  # at least 10ms

    def test_is_finished_false_initially(self):
        span = _make_span()
        assert span.is_finished is False

    def test_is_finished_true_after_finish(self):
        span = _make_span()
        span.finish()
        assert span.is_finished is True

    def test_finish_is_idempotent(self):
        span = _make_span()
        span.finish()
        first_end = span.end_time
        span.finish()
        assert span.end_time == first_end

    def test_set_attribute_stores_value(self):
        span = _make_span()
        span.set_attribute("http.method", "GET")
        assert span.attributes["http.method"] == "GET"

    def test_set_attribute_returns_self(self):
        span = _make_span()
        result = span.set_attribute("key", "val")
        assert result is span

    def test_set_attributes_bulk(self):
        span = _make_span()
        span.set_attributes({"http.status": 200, "db.type": "sql"})
        assert span.attributes["http.status"] == 200
        assert span.attributes["db.type"] == "sql"

    def test_set_attributes_returns_self(self):
        span = _make_span()
        result = span.set_attributes({"a": 1})
        assert result is span

    def test_chaining_api(self):
        span = (
            _make_span().set_attribute("method", "POST").set_attributes({"code": 201})
        )
        assert span.attributes["method"] == "POST"
        assert span.attributes["code"] == 201

    def test_add_event_appends(self):
        span = _make_span()
        span.add_event("cache.hit", {"key": "user:1"})
        assert len(span.events) == 1
        assert span.events[0]["name"] == "cache.hit"
        assert span.events[0]["attributes"]["key"] == "user:1"

    def test_add_event_multiple(self):
        span = _make_span()
        span.add_event("start")
        span.add_event("end")
        assert len(span.events) == 2

    def test_add_event_returns_self(self):
        span = _make_span()
        result = span.add_event("ev")
        assert result is span

    def test_set_status_ok(self):
        span = _make_span()
        span.set_status(SpanStatus.OK)
        assert span.status is SpanStatus.OK
        assert span.status_message == ""

    def test_set_status_error_with_message(self):
        span = _make_span()
        span.set_status(SpanStatus.ERROR, "something broke")
        assert span.status is SpanStatus.ERROR
        assert span.status_message == "something broke"

    def test_set_status_returns_self(self):
        span = _make_span()
        result = span.set_status(SpanStatus.OK)
        assert result is span

    def test_record_exception_sets_error_status(self):
        span = _make_span()
        span.record_exception(ValueError("bad input"))
        assert span.status is SpanStatus.ERROR
        assert "bad input" in span.status_message

    def test_record_exception_appends_event(self):
        span = _make_span()
        span.record_exception(RuntimeError("crash"))
        exception_events = [e for e in span.events if e["name"] == "exception"]
        assert len(exception_events) == 1
        attrs = exception_events[0]["attributes"]
        assert attrs["exception.type"] == "RuntimeError"
        assert attrs["exception.message"] == "crash"

    def test_record_exception_returns_self(self):
        span = _make_span()
        result = span.record_exception(Exception("oops"))
        assert result is span

    def test_to_dict_has_required_keys(self):
        span = _make_span()
        span.finish()
        d = span.to_dict()
        required = {
            "name",
            "trace_id",
            "span_id",
            "parent_span_id",
            "kind",
            "status",
            "status_message",
            "start_time",
            "end_time",
            "duration_ms",
            "attributes",
            "events",
        }
        assert required.issubset(set(d.keys()))

    def test_to_dict_kind_is_value_string(self):
        span = Span(name="svc", context=_make_context(), kind=SpanKind.SERVER)
        span.finish()
        d = span.to_dict()
        assert d["kind"] == "server"

    def test_to_dict_status_is_value_string(self):
        span = _make_span()
        span.set_status(SpanStatus.OK)
        span.finish()
        d = span.to_dict()
        assert d["status"] == "ok"

    def test_to_dict_name_matches(self):
        span = _make_span(name="db.query")
        d = span.to_dict()
        assert d["name"] == "db.query"
