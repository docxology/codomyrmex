"""Test Checkpoint save+load+verify cycle."""

import json
import tempfile
from pathlib import Path

import pytest

from codomyrmex.agents.transport.checkpoint import Checkpoint, StateDelta
from codomyrmex.agents.transport.serializer import AgentSerializer, AgentSnapshot


def test_checkpoint_save_load_verify():
    """Test full save -> load -> verify cycle for Checkpoint."""
    serializer = AgentSerializer()

    # Create a snapshot with realistic data
    snapshot = serializer.snapshot(
        agent_id="test-agent-1",
        agent_type="ThinkingAgent",
        config={"depth": 3, "temperature": 0.7},
        traces=[
            {"step": 1, "thought": "analyze input"},
            {"step": 2, "thought": "formulate response"},
        ],
        memory={"key1": "value1", "key2": "value2"},
        metadata={"session": "test-001"},
    )

    ckpt = Checkpoint(snapshot=snapshot)
    assert ckpt.checkpoint_id.startswith("ckpt-test-agent-1")

    # Save to a temp file
    path = Path(tempfile.mktemp(suffix=".json"))
    ckpt.save(path)

    # Verify file exists and is valid JSON
    assert path.exists()
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["checkpoint_id"] == ckpt.checkpoint_id
    assert raw["snapshot"]["agent_id"] == "test-agent-1"
    assert raw["snapshot"]["config"]["depth"] == 3

    # Load it back
    restored = Checkpoint.load(path)
    assert restored.checkpoint_id == ckpt.checkpoint_id
    assert restored.snapshot.agent_id == "test-agent-1"
    assert restored.snapshot.config == {"depth": 3, "temperature": 0.7}
    assert len(restored.snapshot.traces) == 2
    assert restored.snapshot.memory == {"key1": "value1", "key2": "value2"}

    # Verify diff between original and restored (should be near-zero)
    delta = ckpt.diff(restored)
    # Config and traces are identical, memory is identical
    assert delta.config_changed is False
    assert delta.traces_added == 0
    assert delta.memory_keys_added == []
    assert delta.memory_keys_removed == []
    assert delta.memory_keys_modified == []
    assert delta.has_changes is False

    # Cleanup
    path.unlink(missing_ok=True)


def test_checkpoint_diff_detects_changes():
    """Verify that diff() correctly identifies changes."""
    base_snapshot = AgentSnapshot(
        agent_id="agent-1",
        config={"depth": 3},
        traces=[{"step": 1}],
        memory={"a": 1, "b": 2},
    )
    changed_snapshot = AgentSnapshot(
        agent_id="agent-1",
        config={"depth": 5},  # changed
        traces=[{"step": 1}, {"step": 2}],  # added one
        memory={"a": 1, "c": 3},  # b removed, c added, a unchanged
    )

    base = Checkpoint(snapshot=base_snapshot)
    changed = Checkpoint(snapshot=changed_snapshot)

    delta = base.diff(changed)
    assert delta.config_changed is True
    assert delta.traces_added == 1
    assert "c" in delta.memory_keys_added
    assert "b" in delta.memory_keys_removed
    assert delta.memory_keys_modified == []  # nothing modified, only add/remove
    assert delta.has_changes is True
