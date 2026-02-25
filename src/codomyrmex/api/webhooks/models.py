import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Enums
# ---------------------------------------------------------------------------


class WebhookEventType(Enum):
    """Types of webhook events that can be emitted."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    CUSTOM = "custom"


class WebhookStatus(Enum):
    """Delivery status of a webhook invocation."""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class SignatureAlgorithm(Enum):
    """Supported HMAC signature algorithms for webhook payloads."""

    HMAC_SHA256 = "hmac_sha256"
    HMAC_SHA512 = "hmac_sha512"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class WebhookEvent:
    """Represents a single webhook event to be dispatched.

    Attributes:
        event_type: The category of the event.
        payload: Arbitrary data associated with the event.
        event_id: Unique identifier for the event (auto-generated UUID4).
        timestamp: When the event was created (auto-generated).
        source: Optional identifier for the system that produced the event.
    """

    event_type: WebhookEventType
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize the event to a JSON-compatible dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }

    def to_json(self) -> str:
        """Serialize the event to a JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)


@dataclass
class WebhookConfig:
    """Configuration for a registered webhook endpoint.

    Attributes:
        url: The target URL for webhook delivery.
        secret: Shared secret used to sign payloads.
        events: Event types this webhook subscribes to.
        max_retries: Maximum number of delivery retry attempts.
        retry_delay: Base delay in seconds between retry attempts.
        timeout: HTTP request timeout in seconds.
        signature_algorithm: Algorithm used for payload signing.
        active: Whether this webhook is currently active.
    """

    url: str
    secret: str
    events: list[WebhookEventType] = field(default_factory=list)
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    signature_algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256
    active: bool = True


@dataclass
class DeliveryResult:
    """Result of a single webhook delivery attempt.

    Attributes:
        webhook_id: Identifier of the webhook that was targeted.
        event_id: Identifier of the event that was dispatched.
        status: Delivery status outcome.
        status_code: HTTP status code returned by the endpoint (if any).
        attempt: Which attempt number this result represents (1-based).
        error: Error message if the delivery failed.
        timestamp: When the delivery attempt occurred (auto-generated).
    """

    webhook_id: str
    event_id: str
    status: WebhookStatus
    status_code: int | None = None
    attempt: int = 1
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the delivery result to a dictionary."""
        return {
            "webhook_id": self.webhook_id,
            "event_id": self.event_id,
            "status": self.status.value,
            "status_code": self.status_code,
            "attempt": self.attempt,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


# ---------------------------------------------------------------------------
