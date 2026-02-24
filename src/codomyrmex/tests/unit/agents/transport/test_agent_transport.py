"""Tests for Sprint 31: Agent Serialization & Transport.

Covers AgentSerializer round-trips, HMAC verification, Checkpoint
save/load/diff, and TransportMessage wire format.
"""

import json
import os
import pytest
import tempfile

from codomyrmex.agents.transport.checkpoint import Checkpoint, StateDelta
from codomyrmex.agents.transport.deserializer import AgentDeserializer, IntegrityError
from codomyrmex.agents.transport.protocol import (
    MessageHeader,
    MessageType,
    TransportMessage,
)
from codomyrmex.agents.transport.serializer import AgentSerializer, AgentSnapshot


# ─── AgentSerializer ──────────────────────────────────────────────────

class TestAgentSerializer:
    """Test suite for AgentSerializer."""

    def test_round_trip(self):
        """serialize → deserialize preserves state."""
        serializer = AgentSerializer()
        snapshot = serializer.snapshot(
            agent_id="agent-1",
            agent_type="ThinkingAgent",
            config={"depth": 3, "model": "gpt-4"},
            traces=[{"step": 1, "thought": "analyze"}],
            memory={"key": "value", "count": 42},
        )
        data = serializer.serialize(snapshot)
        restored = serializer.deserialize_snapshot(data)

        assert restored.agent_id == "agent-1"
        assert restored.agent_type == "ThinkingAgent"
        assert restored.config == {"depth": 3, "model": "gpt-4"}
        assert restored.traces == [{"step": 1, "thought": "analyze"}]
        assert restored.memory == {"key": "value", "count": 42}

    def test_compact_json(self):
        """Serialized output uses compact JSON (no whitespace)."""
        serializer = AgentSerializer()
        snapshot = serializer.snapshot(agent_id="a", config={"x": 1})
        data = serializer.serialize(snapshot)
        text = data.decode("utf-8")
        assert "  " not in text  # No indentation

    def test_empty_snapshot(self):
        """Test functionality: empty snapshot."""
        serializer = AgentSerializer()
        snapshot = serializer.snapshot(agent_id="empty")
        data = serializer.serialize(snapshot)
        restored = serializer.deserialize_snapshot(data)
        assert restored.agent_id == "empty"
        assert restored.config == {}


# ─── AgentDeserializer + HMAC ─────────────────────────────────────────

class TestAgentDeserializer:
    """Test suite for AgentDeserializer."""

    def test_sign_and_verify(self):
        """HMAC signing and verification succeeds."""
        serializer = AgentSerializer()
        deserializer = AgentDeserializer()
        snapshot = serializer.snapshot(agent_id="a", config={"x": 1})
        data = serializer.serialize(snapshot)

        sig = deserializer.sign(data, key="secret")
        assert deserializer.verify_signed(data, sig, key="secret") is True

    def test_tampered_payload_rejected(self):
        """Modified payload fails HMAC verification."""
        serializer = AgentSerializer()
        deserializer = AgentDeserializer()
        snapshot = serializer.snapshot(agent_id="a", config={"x": 1})
        data = serializer.serialize(snapshot)
        sig = deserializer.sign(data, key="secret")

        # Tamper with data
        tampered = data + b"TAMPERED"
        with pytest.raises(IntegrityError):
            deserializer.verify_signed(tampered, sig, key="secret")

    def test_deserialize_verified(self):
        """deserialize_verified round-trips with HMAC check."""
        serializer = AgentSerializer()
        deserializer = AgentDeserializer()
        snapshot = serializer.snapshot(agent_id="secure", config={"key": "val"})
        data = serializer.serialize(snapshot)
        sig = deserializer.sign(data, key="mykey")

        restored = deserializer.deserialize_verified(data, sig, key="mykey")
        assert restored.agent_id == "secure"


# ─── TransportMessage ────────────────────────────────────────────────

class TestTransportMessage:
    """Test suite for TransportMessage."""

    def test_round_trip(self):
        """to_bytes → from_bytes preserves message."""
        msg = TransportMessage(
            header=MessageHeader(
                message_type=MessageType.TASK_REQUEST,
                source="node-a",
                destination="node-b",
            ),
            payload={"task": "analyze", "priority": 1},
        )
        data = msg.to_bytes()
        restored = TransportMessage.from_bytes(data)
        assert restored.header.source == "node-a"
        assert restored.payload["task"] == "analyze"

    def test_sign_verify(self):
        """Test functionality: sign verify."""
        msg = TransportMessage(payload={"data": "sensitive"})
        msg.sign("secret-key")
        assert msg.signature != ""
        assert msg.verify("secret-key") is True

    def test_tampered_verify_fails(self):
        """Test functionality: tampered verify fails."""
        msg = TransportMessage(payload={"data": "original"})
        msg.sign("secret-key")
        msg.payload["data"] = "tampered"
        assert msg.verify("secret-key") is False

    def test_message_types(self):
        """Test functionality: message types."""
        for mt in MessageType:
            msg = TransportMessage(header=MessageHeader(message_type=mt))
            data = msg.to_bytes()
            restored = TransportMessage.from_bytes(data)
            assert restored.header.message_type == mt


# ─── Checkpoint ───────────────────────────────────────────────────────

class TestCheckpoint:
    """Test suite for Checkpoint."""

    def test_save_and_load(self, tmp_path):
        """Checkpoint save → load preserves state."""
        snapshot = AgentSnapshot(
            agent_id="agent-1",
            config={"depth": 3},
            memory={"fact": "earth is round"},
        )
        ckpt = Checkpoint(snapshot=snapshot)
        path = tmp_path / "test.ckpt.json"
        ckpt.save(path)

        loaded = Checkpoint.load(path)
        assert loaded.snapshot.agent_id == "agent-1"
        assert loaded.snapshot.config == {"depth": 3}
        assert loaded.snapshot.memory["fact"] == "earth is round"

    def test_diff_no_changes(self):
        """Test functionality: diff no changes."""
        snap = AgentSnapshot(agent_id="a", config={"x": 1}, memory={"k": "v"})
        ckpt1 = Checkpoint(snapshot=snap)
        ckpt2 = Checkpoint(snapshot=snap)
        delta = ckpt1.diff(ckpt2)
        assert delta.has_changes is False

    def test_diff_detects_changes(self):
        """Test functionality: diff detects changes."""
        snap1 = AgentSnapshot(agent_id="a", config={"x": 1}, memory={"k": "v1"})
        snap2 = AgentSnapshot(
            agent_id="a",
            config={"x": 2},
            memory={"k": "v2", "new": "entry"},
            traces=[{"step": 1}],
        )
        ckpt1 = Checkpoint(snapshot=snap1)
        ckpt2 = Checkpoint(snapshot=snap2)
        delta = ckpt1.diff(ckpt2)

        assert delta.has_changes is True
        assert delta.config_changed is True
        assert delta.traces_added == 1
        assert "new" in delta.memory_keys_added
        assert "k" in delta.memory_keys_modified

    def test_checkpoint_id_auto_generated(self):
        """Test functionality: checkpoint id auto generated."""
        snap = AgentSnapshot(agent_id="test-agent")
        ckpt = Checkpoint(snapshot=snap)
        assert "test-agent" in ckpt.checkpoint_id
