"""
Unit tests for telemetry.spans — Zero-Mock compliant.

Covers: SpanContext (to_dict/new_root/child), SpanEvent (to_dict), SpanLink,
SpanStatus constants, Span (start/end/set_attribute/set_attributes/add_event/
add_link/set_status/record_exception/duration_ms/to_dict),
get/set_current_span, Tracer (start_span/span context manager/wrap decorator),
SpanProcessor (process/get_spans/clear/get_trace), BatchSpanProcessor
(process/force_flush), create_tracer.
"""

import pytest

from codomyrmex.telemetry.spans import (
    BatchSpanProcessor,
    Span,
    SpanContext,
    SpanEvent,
    SpanLink,
    SpanProcessor,
    SpanStatus,
    Tracer,
    create_tracer,
    get_current_span,
    set_current_span,
)

# ── SpanContext ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSpanContext:
    def test_to_dict_keys(self):
        ctx = SpanContext(trace_id="t1", span_id="s1")
        d = ctx.to_dict()
        assert "trace_id" in d
        assert "span_id" in d
        assert "parent_span_id" in d
        assert "sampled" in d

    def test_to_dict_values(self):
        ctx = SpanContext(trace_id="abc", span_id="def", parent_span_id="ghi")
        d = ctx.to_dict()
        assert d["trace_id"] == "abc"
        assert d["span_id"] == "def"
        assert d["parent_span_id"] == "ghi"

    def test_default_sampled_true(self):
        ctx = SpanContext(trace_id="t", span_id="s")
        assert ctx.sampled is True

    def test_new_root_creates_unique_ids(self):
        ctx1 = SpanContext.new_root()
        ctx2 = SpanContext.new_root()
        assert ctx1.trace_id != ctx2.trace_id
        assert ctx1.span_id != ctx2.span_id

    def test_new_root_no_parent(self):
        ctx = SpanContext.new_root()
        assert ctx.parent_span_id is None

    def test_child_shares_trace_id(self):
        root = SpanContext.new_root()
        child = root.child()
        assert child.trace_id == root.trace_id

    def test_child_has_different_span_id(self):
        root = SpanContext.new_root()
        child = root.child()
        assert child.span_id != root.span_id

    def test_child_parent_is_root_span_id(self):
        root = SpanContext.new_root()
        child = root.child()
        assert child.parent_span_id == root.span_id

    def test_child_inherits_sampled(self):
        root = SpanContext(trace_id="t", span_id="s", sampled=False)
        child = root.child()
        assert child.sampled is False


# ── SpanEvent ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSpanEvent:
    def test_to_dict_has_name(self):
        e = SpanEvent(name="my_event")
        d = e.to_dict()
        assert d["name"] == "my_event"

    def test_to_dict_has_timestamp(self):
        e = SpanEvent(name="e")
        d = e.to_dict()
        assert "timestamp" in d
        assert isinstance(d["timestamp"], str)

    def test_to_dict_has_attributes(self):
        e = SpanEvent(name="e", attributes={"key": "val"})
        d = e.to_dict()
        assert d["attributes"]["key"] == "val"

    def test_default_attributes_empty(self):
        e = SpanEvent(name="e")
        assert e.attributes == {}


# ── SpanLink ───────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSpanLink:
    def test_fields(self):
        link = SpanLink(trace_id="t1", span_id="s1", attributes={"reason": "follows"})
        assert link.trace_id == "t1"
        assert link.span_id == "s1"
        assert link.attributes["reason"] == "follows"


# ── SpanStatus ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSpanStatus:
    def test_ok_value(self):
        assert SpanStatus.OK == "ok"

    def test_error_value(self):
        assert SpanStatus.ERROR == "error"

    def test_unset_value(self):
        assert SpanStatus.UNSET == "unset"


# ── Span ───────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSpan:
    def test_initial_status_unset(self):
        s = Span("my_op")
        assert s.status == SpanStatus.UNSET

    def test_initial_no_start_time(self):
        s = Span("op")
        assert s.start_time is None

    def test_start_sets_start_time(self):
        s = Span("op").start()
        assert s.start_time is not None

    def test_start_returns_span(self):
        s = Span("op")
        result = s.start()
        assert result is s

    def test_end_sets_end_time(self):
        s = Span("op").start().end()
        assert s.end_time is not None

    def test_end_returns_span(self):
        s = Span("op").start()
        result = s.end()
        assert result is s

    def test_duration_ms_when_not_started(self):
        s = Span("op")
        assert s.duration_ms == 0.0

    def test_duration_ms_positive_after_start_end(self):
        import time
        s = Span("op").start()
        time.sleep(0.001)
        s.end()
        assert s.duration_ms > 0.0

    def test_set_attribute_stores_value(self):
        s = Span("op").set_attribute("env", "prod")
        assert s.attributes["env"] == "prod"

    def test_set_attribute_returns_span(self):
        s = Span("op")
        assert s.set_attribute("k", "v") is s

    def test_set_attributes_bulk(self):
        s = Span("op").set_attributes({"a": 1, "b": 2})
        assert s.attributes["a"] == 1
        assert s.attributes["b"] == 2

    def test_add_event_appended(self):
        s = Span("op").add_event("request_received")
        assert len(s.events) == 1
        assert s.events[0].name == "request_received"

    def test_add_event_with_attributes(self):
        s = Span("op").add_event("cache_hit", {"key": "x"})
        assert s.events[0].attributes["key"] == "x"

    def test_add_event_returns_span(self):
        s = Span("op")
        assert s.add_event("e") is s

    def test_add_link(self):
        ctx = SpanContext.new_root()
        s = Span("op").add_link(ctx, {"type": "follows_from"})
        assert len(s.links) == 1
        assert s.links[0].trace_id == ctx.trace_id

    def test_set_status(self):
        s = Span("op").set_status(SpanStatus.OK)
        assert s.status == SpanStatus.OK

    def test_set_status_with_message(self):
        s = Span("op").set_status(SpanStatus.ERROR, "something failed")
        assert s.status_message == "something failed"

    def test_record_exception_sets_error_status(self):
        s = Span("op").start()
        s.record_exception(ValueError("oops"))
        assert s.status == SpanStatus.ERROR

    def test_record_exception_adds_event(self):
        s = Span("op").start()
        s.record_exception(RuntimeError("boom"))
        assert len(s.events) == 1
        assert s.events[0].name == "exception"

    def test_record_exception_event_has_type(self):
        s = Span("op").start()
        s.record_exception(TypeError("bad type"))
        assert s.events[0].attributes["exception.type"] == "TypeError"

    def test_to_dict_keys(self):
        s = Span("op").start().end()
        d = s.to_dict()
        assert "name" in d
        assert "trace_id" in d
        assert "span_id" in d
        assert "start_time" in d
        assert "end_time" in d
        assert "duration_ms" in d
        assert "attributes" in d
        assert "events" in d
        assert "status" in d

    def test_to_dict_name(self):
        s = Span("my_operation")
        d = s.to_dict()
        assert d["name"] == "my_operation"

    def test_new_span_uses_root_context_by_default(self):
        s = Span("op")
        assert s.context.parent_span_id is None

    def test_span_with_explicit_context(self):
        ctx = SpanContext(trace_id="custom", span_id="span1")
        s = Span("op", context=ctx)
        assert s.context.trace_id == "custom"


# ── get/set_current_span ───────────────────────────────────────────────


@pytest.mark.unit
class TestCurrentSpan:
    def test_initially_none(self):
        set_current_span(None)
        assert get_current_span() is None

    def test_set_and_get(self):
        s = Span("test_span")
        set_current_span(s)
        assert get_current_span() is s
        set_current_span(None)  # cleanup

    def test_set_none_clears(self):
        s = Span("s")
        set_current_span(s)
        set_current_span(None)
        assert get_current_span() is None


# ── Tracer ─────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTracer:
    def test_start_span_returns_span(self):
        t = Tracer("test")
        s = t.start_span("operation")
        assert isinstance(s, Span)
        assert s.name == "operation"

    def test_start_span_is_started(self):
        t = Tracer("test")
        s = t.start_span("op")
        assert s.start_time is not None

    def test_start_span_with_attributes(self):
        t = Tracer("test")
        s = t.start_span("op", attributes={"method": "GET"})
        assert s.attributes["method"] == "GET"

    def test_span_context_manager_yields_span(self):
        t = Tracer("test")
        with t.span("my_op") as s:
            assert isinstance(s, Span)
            assert s.name == "my_op"

    def test_span_context_manager_ends_span(self):
        t = Tracer("test")
        with t.span("op") as s:
            pass
        assert s.end_time is not None

    def test_span_context_manager_sets_ok_on_success(self):
        t = Tracer("test")
        with t.span("op") as s:
            pass
        assert s.status == SpanStatus.OK

    def test_span_context_manager_records_exception(self):
        t = Tracer("test")
        with pytest.raises(RuntimeError):
            with t.span("failing_op") as s:
                raise RuntimeError("test error")
        assert s.status == SpanStatus.ERROR

    def test_span_context_manager_calls_on_span_end(self):
        completed = []
        t = Tracer("test", on_span_end=completed.append)
        with t.span("op"):
            pass
        assert len(completed) == 1
        assert completed[0].name == "op"

    def test_span_restores_current_span_after_exit(self):
        set_current_span(None)
        t = Tracer("test")
        with t.span("outer"):
            with t.span("inner"):
                pass
            assert get_current_span().name == "outer"
        assert get_current_span() is None

    def test_wrap_decorator(self):
        t = Tracer("test")

        @t.wrap("my_function")
        def add(a, b):
            return a + b

        result = add(3, 4)
        assert result == 7

    def test_wrap_decorator_uses_function_name(self):
        completed = []
        t = Tracer("test", on_span_end=completed.append)

        @t.wrap()
        def compute():
            return 42

        compute()
        assert completed[0].name == "compute"

    def test_child_span_shares_trace_id(self):
        t = Tracer("test")
        with t.span("parent") as parent_span:
            parent_trace = parent_span.context.trace_id
            child = t.start_span("child")
            assert child.context.trace_id == parent_trace


# ── SpanProcessor ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestSpanProcessor:
    def test_initially_empty(self):
        p = SpanProcessor()
        assert p.get_spans() == []

    def test_process_adds_span(self):
        p = SpanProcessor()
        s = Span("op").start().end()
        p.process(s)
        assert len(p.get_spans()) == 1

    def test_get_spans_returns_copy(self):
        p = SpanProcessor()
        s = Span("op").start().end()
        p.process(s)
        spans1 = p.get_spans()
        spans2 = p.get_spans()
        assert spans1 is not spans2

    def test_clear_removes_all(self):
        p = SpanProcessor()
        p.process(Span("a").start().end())
        p.process(Span("b").start().end())
        p.clear()
        assert p.get_spans() == []

    def test_get_trace_filters_by_trace_id(self):
        p = SpanProcessor()
        ctx1 = SpanContext.new_root()
        ctx2 = SpanContext.new_root()
        s1 = Span("op1", context=ctx1).start().end()
        s2 = Span("op2", context=ctx2).start().end()
        p.process(s1)
        p.process(s2)
        trace = p.get_trace(ctx1.trace_id)
        assert len(trace) == 1
        assert trace[0].name == "op1"


# ── BatchSpanProcessor ─────────────────────────────────────────────────


@pytest.mark.unit
class TestBatchSpanProcessor:
    def test_process_accumulates_in_batch(self):
        exported = []
        p = BatchSpanProcessor(
            exporter=exported.extend,
            max_batch_size=10,
            flush_interval=100.0,
        )
        p.process(Span("op1").start().end())
        # Not yet flushed since batch size < max_batch_size
        assert len(exported) == 0

    def test_force_flush_exports_batch(self):
        exported = []
        p = BatchSpanProcessor(
            exporter=exported.extend,
            max_batch_size=10,
            flush_interval=100.0,
        )
        p.process(Span("op").start().end())
        p.force_flush()
        assert len(exported) == 1

    def test_flush_on_max_batch_size(self):
        exported = []
        p = BatchSpanProcessor(
            exporter=exported.extend,
            max_batch_size=3,
            flush_interval=100.0,
        )
        for i in range(3):
            p.process(Span(f"op{i}").start().end())
        # Should have auto-flushed
        assert len(exported) == 3

    def test_force_flush_moves_to_spans(self):
        exported = []
        p = BatchSpanProcessor(
            exporter=exported.extend,
            max_batch_size=10,
            flush_interval=100.0,
        )
        p.process(Span("op").start().end())
        p.force_flush()
        assert len(p.get_spans()) == 1


# ── create_tracer ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestCreateTracer:
    def test_returns_tracer(self):
        t = create_tracer("my_tracer")
        assert isinstance(t, Tracer)

    def test_tracer_name_set(self):
        t = create_tracer("svc")
        assert t.name == "svc"

    def test_with_processor_sets_on_span_end(self):
        p = SpanProcessor()
        t = create_tracer("svc", processor=p)
        assert t.on_span_end is not None

    def test_without_processor_no_on_span_end(self):
        t = create_tracer("svc")
        assert t.on_span_end is None

    def test_spans_collected_via_processor(self):
        p = SpanProcessor()
        t = create_tracer("svc", processor=p)
        with t.span("op"):
            pass
        assert len(p.get_spans()) == 1
