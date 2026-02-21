"""Agent transport protocol — wire format for agent messages.

Defines the AgentMessage envelope with header, payload, and
optional HMAC signature for integrity verification.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MessageType(Enum):
    """Types of transport messages."""

    SNAPSHOT = "snapshot"
    CHECKPOINT = "checkpoint"
    TASK_REQUEST = "task_request"
    TASK_RESULT = "task_result"
    HEARTBEAT = "heartbeat"
    CONTROL = "control"


@dataclass
class MessageHeader:
    """Header for a transport message.

    Attributes:
        message_id: Unique message identifier.
        message_type: Type of message.
        version: Protocol version.
        correlation_id: For request-response linking.
        timestamp: Creation timestamp.
        source: Source agent/node identifier.
        destination: Target agent/node identifier.
    """

    message_id: str = ""
    message_type: MessageType = MessageType.SNAPSHOT
    version: str = "1.0"
    correlation_id: str = ""
    timestamp: float = 0.0
    source: str = ""
    destination: str = ""

    def __post_init__(self) -> None:
        if not self.message_id:
            self.message_id = f"msg-{uuid.uuid4().hex[:12]}"
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class TransportMessage:
    """Wire format for agent transport.

    Contains a header, JSON-serializable payload, and optional
    HMAC-SHA256 signature for integrity.

    Attributes:
        header: Message metadata.
        payload: Message content.
        signature: HMAC-SHA256 hex digest (empty = unsigned).
    """

    header: MessageHeader = field(default_factory=MessageHeader)
    payload: dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    def to_bytes(self) -> bytes:
        """Serialize to JSON bytes."""
        data = {
            "header": {
                "message_id": self.header.message_id,
                "message_type": self.header.message_type.value,
                "version": self.header.version,
                "correlation_id": self.header.correlation_id,
                "timestamp": self.header.timestamp,
                "source": self.header.source,
                "destination": self.header.destination,
            },
            "payload": self.payload,
            "signature": self.signature,
        }
        return json.dumps(data, separators=(",", ":")).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> TransportMessage:
        """Deserialize from JSON bytes."""
        raw = json.loads(data)
        header = MessageHeader(
            message_id=raw["header"]["message_id"],
            message_type=MessageType(raw["header"]["message_type"]),
            version=raw["header"]["version"],
            correlation_id=raw["header"]["correlation_id"],
            timestamp=raw["header"]["timestamp"],
            source=raw["header"]["source"],
            destination=raw["header"]["destination"],
        )
        return cls(
            header=header,
            payload=raw.get("payload", {}),
            signature=raw.get("signature", ""),
        )

    def sign(self, key: str) -> None:
        """Sign the message payload with HMAC-SHA256.

        Args:
            key: Secret key for signing.
        """
        payload_bytes = json.dumps(
            self.payload, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        self.signature = hmac.new(
            key.encode("utf-8"), payload_bytes, hashlib.sha256,
        ).hexdigest()

    def verify(self, key: str) -> bool:
        """Verify the HMAC signature.

        Args:
            key: Secret key for verification.

        Returns:
            True if signature is valid.
        """
        if not self.signature:
            return False
        payload_bytes = json.dumps(
            self.payload, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        expected = hmac.new(
            key.encode("utf-8"), payload_bytes, hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(self.signature, expected)

    @property
    def size_bytes(self) -> int:
        """Size of the serialized message in bytes."""
        return len(self.to_bytes())


__all__ = ["MessageHeader", "MessageType", "TransportMessage"]
