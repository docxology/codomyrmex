"""Agent serialization and transport.

Provides portable agent state serialization, HMAC-verified
deserialization, wire-format protocol, and durable checkpointing.
"""

from codomyrmex.agents.transport.checkpoint import Checkpoint, StateDelta
from codomyrmex.agents.transport.deserializer import AgentDeserializer, IntegrityError
from codomyrmex.agents.transport.protocol import (
    MessageHeader,
    MessageType,
    TransportMessage,
)
from codomyrmex.agents.transport.serializer import AgentSerializer, AgentSnapshot

__all__ = [
    "AgentDeserializer",
    "AgentSerializer",
    "AgentSnapshot",
    "Checkpoint",
    "IntegrityError",
    "MessageHeader",
    "MessageType",
    "StateDelta",
    "TransportMessage",
]
