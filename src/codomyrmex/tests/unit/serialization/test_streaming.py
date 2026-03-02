"""
Unit tests for serialization.streaming — Zero-Mock compliant.

Covers: stream_jsonl_write / stream_jsonl_read (round-trip, count,
flush_every branch, empty iterator, blank lines skipped),
stream_csv_write / stream_csv_read (round-trip, explicit fieldnames,
empty iterator), chunked_json_write (single/multiple items, empty,
returns count), StreamBuffer (add, auto-flush on max_size, manual flush,
flush_callback invoked, pending, total_flushed, empty-flush callback
not invoked).
"""

import json
import tempfile
from pathlib import Path

import pytest

from codomyrmex.serialization.streaming import (
    StreamBuffer,
    chunked_json_write,
    stream_csv_read,
    stream_csv_write,
    stream_jsonl_read,
    stream_jsonl_write,
)


def _tmp_path(suffix: str = ".tmp") -> Path:
    f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    f.close()
    return Path(f.name)


# ── stream_jsonl_write / read ─────────────────────────────────────────


@pytest.mark.unit
class TestStreamJsonl:
    def test_round_trip(self):
        items = [{"a": 1}, {"b": 2}, {"c": 3}]
        p = _tmp_path(".jsonl")
        try:
            count = stream_jsonl_write(p, iter(items))
            assert count == 3
            result = list(stream_jsonl_read(p))
            assert result == items
        finally:
            p.unlink()

    def test_returns_item_count(self):
        p = _tmp_path(".jsonl")
        try:
            count = stream_jsonl_write(p, iter([{}, {}, {}, {}]))
            assert count == 4
        finally:
            p.unlink()

    def test_empty_iterator_writes_nothing(self):
        p = _tmp_path(".jsonl")
        try:
            count = stream_jsonl_write(p, iter([]))
            assert count == 0
            result = list(stream_jsonl_read(p))
            assert result == []
        finally:
            p.unlink()

    def test_flush_every_branch(self):
        """flush_every=2 triggers flush for each pair — still writes all items."""
        items = [{"i": i} for i in range(6)]
        p = _tmp_path(".jsonl")
        try:
            count = stream_jsonl_write(p, iter(items), flush_every=2)
            assert count == 6
            result = list(stream_jsonl_read(p))
            assert result == items
        finally:
            p.unlink()

    def test_non_serializable_uses_str(self):
        """default=str in json.dumps converts unknown types."""
        p = _tmp_path(".jsonl")
        try:
            stream_jsonl_write(p, iter([{"obj": object()}]))
            lines = p.read_text().strip().split("\n")
            assert len(lines) == 1
        finally:
            p.unlink()

    def test_read_skips_blank_lines(self):
        p = _tmp_path(".jsonl")
        try:
            p.write_text('{"x": 1}\n\n{"y": 2}\n')
            result = list(stream_jsonl_read(p))
            assert len(result) == 2
            assert result[0] == {"x": 1}
            assert result[1] == {"y": 2}
        finally:
            p.unlink()

    def test_large_batch(self):
        items = [{"n": i} for i in range(500)]
        p = _tmp_path(".jsonl")
        try:
            count = stream_jsonl_write(p, iter(items), flush_every=100)
            assert count == 500
            result = list(stream_jsonl_read(p))
            assert len(result) == 500
        finally:
            p.unlink()


# ── stream_csv_write / read ───────────────────────────────────────────


@pytest.mark.unit
class TestStreamCsv:
    def test_round_trip(self):
        items = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        p = _tmp_path(".csv")
        try:
            count = stream_csv_write(p, iter(items))
            assert count == 2
            result = list(stream_csv_read(p))
            assert result == items
        finally:
            p.unlink()

    def test_explicit_fieldnames(self):
        items = [{"x": "1", "y": "2"}, {"x": "3", "y": "4"}]
        p = _tmp_path(".csv")
        try:
            stream_csv_write(p, iter(items), fieldnames=["x", "y"])
            result = list(stream_csv_read(p))
            assert result[0]["x"] == "1"
        finally:
            p.unlink()

    def test_returns_count(self):
        p = _tmp_path(".csv")
        try:
            count = stream_csv_write(p, iter([{"k": "v"}] * 7))
            assert count == 7
        finally:
            p.unlink()

    def test_empty_iterator_returns_zero(self):
        p = _tmp_path(".csv")
        try:
            count = stream_csv_write(p, iter([]))
            assert count == 0
        finally:
            p.unlink()

    def test_csv_has_header_row(self):
        p = _tmp_path(".csv")
        try:
            stream_csv_write(p, iter([{"col": "val"}]))
            lines = p.read_text().strip().split("\n")
            assert lines[0] == "col"
        finally:
            p.unlink()


# ── chunked_json_write ────────────────────────────────────────────────


@pytest.mark.unit
class TestChunkedJsonWrite:
    def test_writes_valid_json_array(self):
        p = _tmp_path(".json")
        try:
            count = chunked_json_write(p, [1, 2, 3])
            assert count == 3
            data = json.loads(p.read_text())
            assert data == [1, 2, 3]
        finally:
            p.unlink()

    def test_single_item(self):
        p = _tmp_path(".json")
        try:
            count = chunked_json_write(p, [{"x": 1}])
            assert count == 1
            data = json.loads(p.read_text())
            assert data == [{"x": 1}]
        finally:
            p.unlink()

    def test_empty_list(self):
        p = _tmp_path(".json")
        try:
            count = chunked_json_write(p, [])
            assert count == 0
            data = json.loads(p.read_text())
            assert data == []
        finally:
            p.unlink()

    def test_returns_item_count(self):
        p = _tmp_path(".json")
        try:
            count = chunked_json_write(p, list(range(50)))
            assert count == 50
        finally:
            p.unlink()

    def test_non_serializable_uses_str(self):
        p = _tmp_path(".json")
        try:
            count = chunked_json_write(p, [object()])
            assert count == 1
        finally:
            p.unlink()


# ── StreamBuffer ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestStreamBuffer:
    def test_initial_pending_zero(self):
        buf = StreamBuffer(max_size=10)
        assert buf.pending == 0

    def test_initial_total_flushed_zero(self):
        buf = StreamBuffer(max_size=10)
        assert buf.total_flushed == 0

    def test_add_increments_pending(self):
        buf = StreamBuffer(max_size=10)
        buf.add("item1")
        assert buf.pending == 1
        buf.add("item2")
        assert buf.pending == 2

    def test_manual_flush_returns_items(self):
        buf = StreamBuffer(max_size=10)
        buf.add("a")
        buf.add("b")
        items = buf.flush()
        assert items == ["a", "b"]

    def test_flush_clears_buffer(self):
        buf = StreamBuffer(max_size=10)
        buf.add("x")
        buf.flush()
        assert buf.pending == 0

    def test_flush_updates_total_flushed(self):
        buf = StreamBuffer(max_size=10)
        buf.add(1)
        buf.add(2)
        buf.add(3)
        buf.flush()
        assert buf.total_flushed == 3

    def test_auto_flush_on_max_size(self):
        buf = StreamBuffer(max_size=3)
        buf.add("a")
        buf.add("b")
        buf.add("c")  # triggers auto-flush (pending was 3 >= max_size=3)
        assert buf.pending == 0
        assert buf.total_flushed == 3

    def test_auto_flush_callback_called(self):
        flushed = []

        def cb(items):
            flushed.extend(items)

        buf = StreamBuffer(max_size=2, flush_callback=cb)
        buf.add(1)
        buf.add(2)  # triggers auto-flush
        assert flushed == [1, 2]

    def test_flush_callback_not_called_on_empty_flush(self):
        called = [False]

        def cb(items):
            called[0] = True

        buf = StreamBuffer(max_size=10, flush_callback=cb)
        buf.flush()  # empty buffer — callback should NOT be called
        assert called[0] is False

    def test_multiple_flushes_accumulate_total(self):
        buf = StreamBuffer(max_size=10)
        for _ in range(3):
            buf.add("x")
            buf.flush()
        assert buf.total_flushed == 3

    def test_add_arbitrary_types(self):
        buf = StreamBuffer(max_size=5)
        buf.add(42)
        buf.add({"k": "v"})
        buf.add([1, 2, 3])
        assert buf.pending == 3

    def test_no_callback_no_error(self):
        buf = StreamBuffer(max_size=2)
        buf.add(1)
        buf.add(2)  # auto-flush with no callback — should not raise
        assert buf.total_flushed == 2
