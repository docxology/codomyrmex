"""
Unit tests for concurrency.dead_letter — Zero-Mock compliant.

Covers: DeadLetterQueue (add, list_entries filtering, replay success/failure/not-found,
_mark_replayed, purge all / purge before timestamp, thread-safety via concurrent adds,
empty-file edge cases).
"""

import tempfile
import threading
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from codomyrmex.concurrency.dead_letter import DeadLetterQueue


def _tmp_dlq() -> tuple[DeadLetterQueue, Path]:
    """Return (dlq, path) with an isolated temp JSONL file."""
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl")
    f.close()
    path = Path(f.name)
    return DeadLetterQueue(path=path), path


@pytest.mark.unit
class TestDeadLetterQueueAdd:
    def test_add_returns_uuid_string(self):
        dlq, path = _tmp_dlq()
        try:
            entry_id = dlq.add(operation="call_tool", error="timeout")
            assert isinstance(entry_id, str)
            assert len(entry_id) == 36  # UUID4 with dashes
        finally:
            path.unlink(missing_ok=True)

    def test_add_ids_are_unique(self):
        dlq, path = _tmp_dlq()
        try:
            ids = {dlq.add(operation="op", error="err") for _ in range(10)}
            assert len(ids) == 10
        finally:
            path.unlink(missing_ok=True)

    def test_add_persists_to_file(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="call_tool", error="timeout")
            lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
            assert len(lines) == 1
        finally:
            path.unlink(missing_ok=True)

    def test_add_with_args(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", args={"key": "value"}, error="err")
            entries = dlq.list_entries(include_replayed=True)
            assert entries[0]["args"] == {"key": "value"}
        finally:
            path.unlink(missing_ok=True)

    def test_add_with_metadata(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="err", metadata={"correlation_id": "abc"})
            entries = dlq.list_entries(include_replayed=True)
            assert entries[0]["metadata"]["correlation_id"] == "abc"
        finally:
            path.unlink(missing_ok=True)

    def test_add_args_none_defaults_to_empty_dict(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="err")
            entries = dlq.list_entries(include_replayed=True)
            assert entries[0]["args"] == {}
        finally:
            path.unlink(missing_ok=True)

    def test_add_replayed_false_by_default(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="err")
            entries = dlq.list_entries(include_replayed=True)
            assert entries[0]["replayed"] is False
        finally:
            path.unlink(missing_ok=True)

    def test_add_operation_stored(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="my_operation", error="err")
            entries = dlq.list_entries(include_replayed=True)
            assert entries[0]["operation"] == "my_operation"
        finally:
            path.unlink(missing_ok=True)

    def test_add_error_stored(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="something went wrong")
            entries = dlq.list_entries(include_replayed=True)
            assert entries[0]["error"] == "something went wrong"
        finally:
            path.unlink(missing_ok=True)

    def test_add_timestamp_is_iso(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="err")
            entries = dlq.list_entries(include_replayed=True)
            ts = entries[0]["timestamp"]
            assert "T" in ts  # ISO 8601
        finally:
            path.unlink(missing_ok=True)


@pytest.mark.unit
class TestDeadLetterQueueListEntries:
    def test_empty_queue_returns_empty_list(self):
        dlq, path = _tmp_dlq()
        try:
            assert dlq.list_entries() == []
        finally:
            path.unlink(missing_ok=True)

    def test_nonexistent_file_returns_empty(self):
        path = Path(tempfile.mktemp(suffix=".jsonl"))
        dlq = DeadLetterQueue(path=path)
        # File never created
        assert dlq.list_entries() == []

    def test_list_all_entries(self):
        dlq, path = _tmp_dlq()
        try:
            for i in range(3):
                dlq.add(operation=f"op{i}", error="err")
            entries = dlq.list_entries()
            assert len(entries) == 3
        finally:
            path.unlink(missing_ok=True)

    def test_excludes_replayed_by_default(self):
        dlq, path = _tmp_dlq()
        try:
            entry_id = dlq.add(operation="op", error="err")
            dlq.replay(entry_id, callback=lambda op, args: "ok")
            # Default: include_replayed=False
            entries = dlq.list_entries()
            assert entries == []
        finally:
            path.unlink(missing_ok=True)

    def test_include_replayed_true_shows_all(self):
        dlq, path = _tmp_dlq()
        try:
            entry_id = dlq.add(operation="op", error="err")
            dlq.replay(entry_id, callback=lambda op, args: "ok")
            entries = dlq.list_entries(include_replayed=True)
            assert len(entries) == 1
        finally:
            path.unlink(missing_ok=True)

    def test_filter_by_operation(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="tool_a", error="err")
            dlq.add(operation="tool_b", error="err")
            dlq.add(operation="tool_a", error="err")
            entries = dlq.list_entries(operation="tool_a")
            assert len(entries) == 2
            assert all(e["operation"] == "tool_a" for e in entries)
        finally:
            path.unlink(missing_ok=True)

    def test_filter_by_operation_no_match(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="tool_a", error="err")
            entries = dlq.list_entries(operation="tool_z")
            assert entries == []
        finally:
            path.unlink(missing_ok=True)

    def test_filter_by_since(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="err")
            future = datetime.utcnow() + timedelta(days=1)
            entries = dlq.list_entries(since=future)
            assert entries == []
        finally:
            path.unlink(missing_ok=True)

    def test_filter_by_since_includes_current(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="err")
            past = datetime.utcnow() - timedelta(days=1)
            entries = dlq.list_entries(since=past)
            assert len(entries) == 1
        finally:
            path.unlink(missing_ok=True)

    def test_entry_has_id_field(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="err")
            entry = dlq.list_entries()[0]
            assert "id" in entry
        finally:
            path.unlink(missing_ok=True)


@pytest.mark.unit
class TestDeadLetterQueueReplay:
    def test_replay_success_returns_success_true(self):
        dlq, path = _tmp_dlq()
        try:
            entry_id = dlq.add(operation="op", error="err")
            result = dlq.replay(entry_id, callback=lambda op, args: "done")
            assert result["success"] is True
        finally:
            path.unlink(missing_ok=True)

    def test_replay_invokes_callback_with_operation_and_args(self):
        dlq, path = _tmp_dlq()
        try:
            calls = []
            entry_id = dlq.add(
                operation="my_tool", args={"x": 1}, error="err"
            )
            dlq.replay(
                entry_id,
                callback=lambda op, args: calls.append((op, args)),
            )
            assert calls == [("my_tool", {"x": 1})]
        finally:
            path.unlink(missing_ok=True)

    def test_replay_result_contains_callback_return(self):
        dlq, path = _tmp_dlq()
        try:
            entry_id = dlq.add(operation="op", error="err")
            result = dlq.replay(entry_id, callback=lambda op, args: {"answer": 42})
            assert result["result"] == {"answer": 42}
        finally:
            path.unlink(missing_ok=True)

    def test_replay_marks_entry_replayed(self):
        dlq, path = _tmp_dlq()
        try:
            entry_id = dlq.add(operation="op", error="err")
            dlq.replay(entry_id, callback=lambda op, args: None)
            # Entry should now be excluded by default
            assert dlq.list_entries() == []
        finally:
            path.unlink(missing_ok=True)

    def test_replay_not_found_returns_failure(self):
        dlq, path = _tmp_dlq()
        try:
            result = dlq.replay("nonexistent-id", callback=lambda op, args: None)
            assert result["success"] is False
            assert "not found" in result["error"]
        finally:
            path.unlink(missing_ok=True)

    def test_replay_callback_raises_returns_failure(self):
        dlq, path = _tmp_dlq()
        try:
            entry_id = dlq.add(operation="op", error="err")

            def bad_callback(op, args):
                raise RuntimeError("retry failed")

            result = dlq.replay(entry_id, callback=bad_callback)
            assert result["success"] is False
            assert "retry failed" in result["error"]
        finally:
            path.unlink(missing_ok=True)

    def test_replay_callback_raises_does_not_mark_replayed(self):
        dlq, path = _tmp_dlq()
        try:
            entry_id = dlq.add(operation="op", error="err")

            def bad_callback(op, args):
                raise ValueError("boom")

            dlq.replay(entry_id, callback=bad_callback)
            # Entry was NOT marked replayed — still visible
            entries = dlq.list_entries()
            assert len(entries) == 1
        finally:
            path.unlink(missing_ok=True)


@pytest.mark.unit
class TestDeadLetterQueuePurge:
    def test_purge_all_returns_count(self):
        dlq, path = _tmp_dlq()
        try:
            for _ in range(5):
                dlq.add(operation="op", error="err")
            count = dlq.purge()
            assert count == 5
        finally:
            path.unlink(missing_ok=True)

    def test_purge_all_empties_queue(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="err")
            dlq.purge()
            assert dlq.list_entries() == []
        finally:
            path.unlink(missing_ok=True)

    def test_purge_empty_queue_returns_zero(self):
        dlq, path = _tmp_dlq()
        try:
            count = dlq.purge()
            assert count == 0
        finally:
            path.unlink(missing_ok=True)

    def test_purge_before_future_removes_old_entries(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="err")
            future = datetime.utcnow() + timedelta(days=1)
            count = dlq.purge(before=future)
            assert count == 1
            assert dlq.list_entries() == []
        finally:
            path.unlink(missing_ok=True)

    def test_purge_before_past_keeps_entries(self):
        dlq, path = _tmp_dlq()
        try:
            dlq.add(operation="op", error="err")
            past = datetime.utcnow() - timedelta(days=365)
            count = dlq.purge(before=past)
            assert count == 0
            assert len(dlq.list_entries()) == 1
        finally:
            path.unlink(missing_ok=True)

    def test_purge_nonexistent_file_returns_zero(self):
        path = Path(tempfile.mktemp(suffix=".jsonl"))
        dlq = DeadLetterQueue(path=path)
        assert dlq.purge() == 0


@pytest.mark.unit
class TestDeadLetterQueueThreadSafety:
    def test_concurrent_adds_all_persisted(self):
        dlq, path = _tmp_dlq()
        try:
            errors = []

            def add_entries():
                try:
                    for _ in range(10):
                        dlq.add(operation="concurrent_op", error="thread error")
                except Exception as e:
                    errors.append(str(e))

            threads = [threading.Thread(target=add_entries) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert errors == [], f"Thread errors: {errors}"
            entries = dlq.list_entries()
            assert len(entries) == 50
        finally:
            path.unlink(missing_ok=True)
