"""Agent state serialization.

Serializes agent configurations, traces, and memory snapshots
into portable JSON format for transport and checkpointing.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentSnapshot:
    """Point-in-time capture of agent state.

    Attributes:
        agent_id: Agent identifier.
        agent_type: Fully qualified class name.
        config: Agent configuration dict.
        traces: Reasoning traces.
        memory: Memory store snapshot.
        metadata: Additional context.
        timestamp: Snapshot creation time.
        version: Snapshot format version.
    """

    agent_id: str
    agent_type: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    traces: list[dict[str, Any]] = field(default_factory=list)
    memory: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    version: str = "1.0"


class AgentSerializer:
    """Serialize agent state to portable formats.

    Captures configuration, reasoning traces, and memory into
    a JSON-serializable AgentSnapshot.

    Example::

        serializer = AgentSerializer()
        snapshot = serializer.snapshot(
            agent_id="agent-1",
            agent_type="ThinkingAgent",
            config={"depth": 3},
            traces=[{"step": 1, "thought": "analyze"}],
            memory={"key": "value"},
        )
        data = serializer.serialize(snapshot)
        restored = serializer.deserialize_snapshot(data)
    """

    def snapshot(
        self,
        agent_id: str,
        agent_type: str = "",
        config: dict[str, Any] | None = None,
        traces: list[dict[str, Any]] | None = None,
        memory: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentSnapshot:
        """Create a point-in-time snapshot of agent state.

        Args:
            agent_id: Agent identifier.
            agent_type: Agent class name.
            config: Configuration dict.
            traces: Reasoning trace history.
            memory: Memory key-value pairs.
            metadata: Additional context.

        Returns:
            AgentSnapshot capturing current state.
        """
        return AgentSnapshot(
            agent_id=agent_id,
            agent_type=agent_type,
            config=config or {},
            traces=traces or [],
            memory=memory or {},
            metadata=metadata or {},
        )

    def serialize(self, snapshot: AgentSnapshot) -> bytes:
        """Serialize an AgentSnapshot to JSON bytes.

        Args:
            snapshot: The snapshot to serialize.

        Returns:
            UTF-8 encoded JSON bytes.
        """
        data = {
            "agent_id": snapshot.agent_id,
            "agent_type": snapshot.agent_type,
            "config": snapshot.config,
            "traces": snapshot.traces,
            "memory": snapshot.memory,
            "metadata": snapshot.metadata,
            "timestamp": snapshot.timestamp,
            "version": snapshot.version,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def deserialize_snapshot(self, data: bytes) -> AgentSnapshot:
        """Deserialize JSON bytes back to an AgentSnapshot.

        Args:
            data: UTF-8 encoded JSON bytes.

        Returns:
            Reconstructed AgentSnapshot.
        """
        raw = json.loads(data)
        return AgentSnapshot(
            agent_id=raw["agent_id"],
            agent_type=raw.get("agent_type", ""),
            config=raw.get("config", {}),
            traces=raw.get("traces", []),
            memory=raw.get("memory", {}),
            metadata=raw.get("metadata", {}),
            timestamp=raw.get("timestamp", 0.0),
            version=raw.get("version", "1.0"),
        )

    def compact_size(self, snapshot: AgentSnapshot) -> int:
        """Get the serialized size in bytes."""
        return len(self.serialize(snapshot))


__all__ = ["AgentSerializer", "AgentSnapshot"]
