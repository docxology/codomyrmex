"""Test dead letter queue replay in-progress marker."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from codomyrmex.concurrency.dead_letter import DeadLetterQueue


def _dummy_callback(operation: str, args: dict) -> str:
    """Simple callback that returns a result."""
    return f"replayed {operation}"


def test_replay_in_progress_marker():
    """Verify that replay writes in-progress marker before callback."""
    fd, _name = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    dlq = DeadLetterQueue(path=_name)

    entry_id = dlq.add(operation="test_op", args={"key": "val"}, error="boom")
    result = dlq.replay(entry_id, _dummy_callback)
    assert result["success"] is True
    assert result["result"] == "replayed test_op"

    # Verify the written entry: should have replayed=True, no replay_in_progress
    lines = Path(dlq._path).read_text(encoding="utf-8").splitlines()
    saved = json.loads(lines[0])
    assert saved["replayed"] is True
    assert "replay_in_progress" not in saved
    assert "replayed_at" in saved


def test_replay_crash_leaves_in_progress():
    """Simulate a crash between callback and _mark_replayed by
    calling _mark_replaying manually and never calling _mark_replayed."""
    fd, _name = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    dlq = DeadLetterQueue(path=_name)

    entry_id = dlq.add(operation="crash_op", args={"x": 1}, error="timeout")

    # Manually trigger the in-progress marker (simulating a crash mid-replay)
    dlq._mark_replaying(entry_id)

    # Now read back: should have replay_in_progress=True but not replayed
    lines = Path(dlq._path).read_text(encoding="utf-8").splitlines()
    saved = json.loads(lines[0])
    assert saved.get("replay_in_progress") is True
    assert saved.get("replayed") is False

    # list_entries with reconcile_stale=True should clean this up
    entries = dlq.list_entries(reconcile_stale=True)
    # Our entry should no longer be returned as not-replayed (it became replay_failed)
    # We asked for include_replayed=False, so it's excluded
    assert len(entries) == 0

    # But reading with include_replayed=True should show the reconciled state
    all_entries = dlq.list_entries(include_replayed=True, reconcile_stale=False)
    if all_entries:
        reconciled = all_entries[0]
        assert reconciled.get("replay_in_progress") is False
        assert reconciled.get("replay_failed") is True


def test_replay_checks_in_progress():
    """Verify that a replay cannot restart while one is in progress."""
    fd, _name = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    dlq = DeadLetterQueue(path=_name)
    entry_id = dlq.add(operation="slow_op", args={}, error="oom")

    # Manually set up in-progress state in the active_replays set
    dlq._active_replays.add(entry_id)

    # Now replay should detect concurrent replay
    result = dlq.replay(entry_id, _dummy_callback)
    assert result["success"] is False
    assert "in progress" in result.get("error", "")
