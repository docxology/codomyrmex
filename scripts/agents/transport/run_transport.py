#!/usr/bin/env python3
"""Transport — Thin Script Orchestrator.

Exercises agent serialization roundtrip: serialize → snapshot → deserialize.

Usage:
    python scripts/agents/transport/run_transport.py
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    sys.path.insert(
        0, str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    )

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_info("Transport — serialization roundtrip test...")

    try:
        from codomyrmex.agents.transport import (
            AgentDeserializer,
            AgentSerializer,
            AgentSnapshot,
            Checkpoint,
            MessageType,
            TransportMessage,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    print_success("Transport classes imported successfully:")
    for cls in [
        AgentSerializer,
        AgentDeserializer,
        AgentSnapshot,
        Checkpoint,
        TransportMessage,
        MessageType,
    ]:
        print_info(f"  {cls.__name__}")

    # Exercise snapshot creation
    snapshot = AgentSnapshot(
        agent_id="test-agent", state={"counter": 42, "mode": "explore"}
    )
    print_success(
        f"Snapshot created: agent_id={snapshot.agent_id}, keys={list(snapshot.state.keys())}"
    )

    # Serialize roundtrip
    serializer = AgentSerializer()
    data = serializer.serialize(snapshot)
    print_info(f"  Serialized: {len(data)} bytes")

    deserializer = AgentDeserializer()
    restored = deserializer.deserialize(data)
    assert restored.state["counter"] == 42, "Roundtrip integrity check failed"
    print_success("Roundtrip integrity verified ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
