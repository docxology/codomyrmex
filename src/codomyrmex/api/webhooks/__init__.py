"""
Webhooks Submodule

Webhook dispatch and receipt management for event-driven APIs.
Provides webhook registration, signature verification, event dispatching,
and retry logic for reliable webhook delivery.
"""

__version__ = "0.1.0"

import hashlib
import hmac
import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from collections.abc import Callable

# ---------------------------------------------------------------------------
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
# Abstract base class
# ---------------------------------------------------------------------------


class WebhookTransport(ABC):
    """Abstract transport layer for sending webhook payloads.

    Implementations must provide a ``send`` method that delivers a payload
    to a target URL and returns the HTTP status code and response body.
    """

    @abstractmethod
    def send(
        self,
        url: str,
        payload: str,
        headers: dict[str, str],
        timeout: float,
    ) -> tuple[int, str]:
        """Send a webhook payload to the given URL.

        Args:
            url: Target endpoint URL.
            payload: Serialized payload body (JSON string).
            headers: HTTP headers to include with the request.
            timeout: Request timeout in seconds.

        Returns:
            A tuple of (status_code, response_body).
        """
        pass


# ---------------------------------------------------------------------------
# Concrete classes
# ---------------------------------------------------------------------------


class HTTPWebhookTransport(WebhookTransport):
    """Callback-based webhook transport for testing and in-process dispatch.

    Instead of making real HTTP requests this transport delegates delivery
    to a user-supplied callable, making it ideal for unit tests and
    local event buses.

    Args:
        handler: A callable that receives ``(url, payload, headers, timeout)``
            and returns a tuple of ``(status_code, response_body)``.
    """

    def __init__(
        self,
        handler: Callable[
            [str, str, dict[str, str], float], tuple[int, str]
        ],
    ) -> None:
        """Execute   Init   operations natively."""
        self._handler = handler

    def send(
        self,
        url: str,
        payload: str,
        headers: dict[str, str],
        timeout: float,
    ) -> tuple[int, str]:
        """Delegate delivery to the configured handler callable.

        Args:
            url: Target endpoint URL.
            payload: Serialized payload body (JSON string).
            headers: HTTP headers to include with the request.
            timeout: Request timeout in seconds.

        Returns:
            A tuple of (status_code, response_body) as returned by the handler.
        """
        return self._handler(url, payload, headers, timeout)


class WebhookSignature:
    """Utility for signing and verifying webhook payloads using HMAC.

    All methods are static so that signing/verification can be performed
    without instantiation.
    """

    _ALGORITHM_MAP: dict[SignatureAlgorithm, str] = {
        SignatureAlgorithm.HMAC_SHA256: "sha256",
        SignatureAlgorithm.HMAC_SHA512: "sha512",
    }

    @staticmethod
    def sign(
        payload: str,
        secret: str,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
    ) -> str:
        """Create an HMAC signature for the given payload.

        Args:
            payload: The string payload to sign.
            secret: The shared secret key.
            algorithm: The HMAC algorithm to use.

        Returns:
            Hex-encoded HMAC signature string.
        """
        hash_func = WebhookSignature._ALGORITHM_MAP[algorithm]
        return hmac.new(
            key=secret.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=getattr(hashlib, hash_func),
        ).hexdigest()

    @staticmethod
    def verify(
        payload: str,
        secret: str,
        signature: str,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
    ) -> bool:
        """Verify an HMAC signature against a payload.

        Uses constant-time comparison to prevent timing attacks.

        Args:
            payload: The string payload that was signed.
            secret: The shared secret key.
            signature: The signature to verify against.
            algorithm: The HMAC algorithm that was used for signing.

        Returns:
            ``True`` if the signature is valid, ``False`` otherwise.
        """
        expected = WebhookSignature.sign(payload, secret, algorithm)
        return hmac.compare_digest(expected, signature)


class WebhookRegistry:
    """In-memory registry for webhook configurations.

    Stores webhook configs keyed by a string identifier and provides
    lookup, listing, and filtering capabilities.
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._webhooks: dict[str, WebhookConfig] = {}

    def register(self, webhook_id: str, config: WebhookConfig) -> None:
        """Register a new webhook or update an existing one.

        Args:
            webhook_id: Unique identifier for the webhook.
            config: The webhook configuration to store.
        """
        self._webhooks[webhook_id] = config

    def unregister(self, webhook_id: str) -> None:
        """Remove a webhook from the registry.

        Args:
            webhook_id: Identifier of the webhook to remove.

        Raises:
            KeyError: If the webhook_id is not found.
        """
        if webhook_id not in self._webhooks:
            raise KeyError(f"Webhook '{webhook_id}' not found in registry")
        del self._webhooks[webhook_id]

    def get(self, webhook_id: str) -> WebhookConfig | None:
        """Retrieve a webhook config by identifier.

        Args:
            webhook_id: Identifier of the webhook.

        Returns:
            The ``WebhookConfig`` if found, otherwise ``None``.
        """
        return self._webhooks.get(webhook_id)

    def list_all(self) -> dict[str, WebhookConfig]:
        """Return a copy of all registered webhooks.

        Returns:
            Dictionary mapping webhook IDs to their configs.
        """
        return dict(self._webhooks)

    def list_for_event(
        self, event_type: WebhookEventType
    ) -> dict[str, WebhookConfig]:
        """Return all active webhooks subscribed to a given event type.

        A webhook matches if it is active **and** either has the event type
        in its ``events`` list or has an empty ``events`` list (subscribes
        to all events).

        Args:
            event_type: The event type to filter by.

        Returns:
            Dictionary of matching webhook IDs to their configs.
        """
        return {
            wid: config
            for wid, config in self._webhooks.items()
            if config.active
            and (event_type in config.events or len(config.events) == 0)
        }


class WebhookDispatcher:
    """Dispatches webhook events to registered endpoints via a transport.

    Coordinates between the ``WebhookRegistry`` (which webhooks to target),
    the ``WebhookSignature`` class (payload signing), and a
    ``WebhookTransport`` (actual delivery).

    Args:
        registry: The registry to look up webhooks from.
        transport: The transport used to deliver payloads.
    """

    def __init__(
        self,
        registry: WebhookRegistry,
        transport: WebhookTransport,
    ) -> None:
        """Execute   Init   operations natively."""
        self._registry = registry
        self._transport = transport

    @property
    def registry(self) -> WebhookRegistry:
        """Access the underlying webhook registry."""
        return self._registry

    @property
    def transport(self) -> WebhookTransport:
        """Access the underlying transport."""
        return self._transport

    def _build_headers(
        self,
        event: WebhookEvent,
        config: WebhookConfig,
        payload_json: str,
    ) -> dict[str, str]:
        """Build HTTP headers including the HMAC signature.

        Args:
            event: The event being dispatched.
            config: The webhook configuration (contains secret/algorithm).
            payload_json: The serialized JSON payload string.

        Returns:
            Dictionary of header name to header value.
        """
        signature = WebhookSignature.sign(
            payload_json, config.secret, config.signature_algorithm
        )
        return {
            "Content-Type": "application/json",
            "X-Webhook-Event": event.event_type.value,
            "X-Webhook-Event-Id": event.event_id,
            "X-Webhook-Signature": signature,
            "X-Webhook-Signature-Algorithm": config.signature_algorithm.value,
            "X-Webhook-Timestamp": event.timestamp.isoformat(),
        }

    def _deliver(
        self,
        webhook_id: str,
        event: WebhookEvent,
        config: WebhookConfig,
        attempt: int = 1,
    ) -> DeliveryResult:
        """Attempt a single delivery of an event to a webhook endpoint.

        Args:
            webhook_id: Identifier of the target webhook.
            event: The event to deliver.
            config: Configuration of the target webhook.
            attempt: The attempt number (1-based).

        Returns:
            A ``DeliveryResult`` describing the outcome.
        """
        payload_json = event.to_json()
        headers = self._build_headers(event, config, payload_json)

        try:
            status_code, _body = self._transport.send(
                url=config.url,
                payload=payload_json,
                headers=headers,
                timeout=config.timeout,
            )

            if 200 <= status_code < 300:
                return DeliveryResult(
                    webhook_id=webhook_id,
                    event_id=event.event_id,
                    status=WebhookStatus.DELIVERED,
                    status_code=status_code,
                    attempt=attempt,
                )
            else:
                return DeliveryResult(
                    webhook_id=webhook_id,
                    event_id=event.event_id,
                    status=WebhookStatus.FAILED,
                    status_code=status_code,
                    attempt=attempt,
                    error=f"Non-success status code: {status_code}",
                )
        except Exception as exc:
            return DeliveryResult(
                webhook_id=webhook_id,
                event_id=event.event_id,
                status=WebhookStatus.FAILED,
                attempt=attempt,
                error=str(exc),
            )

    def dispatch(self, event: WebhookEvent) -> list[DeliveryResult]:
        """Dispatch an event to all matching registered webhooks.

        Iterates over all active webhooks subscribed to the event type,
        signs the payload, sends via transport, and collects results.

        Args:
            event: The webhook event to dispatch.

        Returns:
            List of ``DeliveryResult`` objects, one per targeted webhook.
        """
        targets = self._registry.list_for_event(event.event_type)
        results: list[DeliveryResult] = []

        for webhook_id, config in targets.items():
            result = self._deliver(webhook_id, event, config, attempt=1)
            results.append(result)

        return results

    def dispatch_with_retry(
        self,
        event: WebhookEvent,
        max_retries: int | None = None,
    ) -> list[DeliveryResult]:
        """Dispatch an event with automatic retries on failure.

        For each targeted webhook, if the initial delivery fails, retries
        up to ``max_retries`` times (defaulting to the webhook's own
        ``max_retries`` config value). A simple linear back-off based on
        the webhook's ``retry_delay`` is applied between attempts.

        Args:
            event: The webhook event to dispatch.
            max_retries: Override for the per-webhook max_retries setting.
                If ``None``, each webhook's own ``max_retries`` is used.

        Returns:
            List of final ``DeliveryResult`` objects, one per targeted
            webhook. Each result reflects the outcome of the last attempt
            (whether successful or the final failure).
        """
        targets = self._registry.list_for_event(event.event_type)
        results: list[DeliveryResult] = []

        for webhook_id, config in targets.items():
            retries = max_retries if max_retries is not None else config.max_retries
            last_result: DeliveryResult | None = None

            for attempt in range(1, retries + 2):  # attempts = retries + 1
                result = self._deliver(
                    webhook_id, event, config, attempt=attempt
                )

                if result.status == WebhookStatus.DELIVERED:
                    last_result = result
                    break

                # Mark as retrying if we have more attempts left
                if attempt <= retries:
                    result.status = WebhookStatus.RETRYING
                    time.sleep(config.retry_delay)

                last_result = result

            if last_result is not None:
                results.append(last_result)

        return results


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------


def create_webhook_registry() -> WebhookRegistry:
    """Create a new, empty webhook registry.

    Returns:
        A fresh ``WebhookRegistry`` instance.
    """
    return WebhookRegistry()


def create_webhook_dispatcher(
    registry: WebhookRegistry | None = None,
    transport: WebhookTransport | None = None,
) -> WebhookDispatcher:
    """Create a webhook dispatcher with optional defaults.

    If no registry is provided, a new empty one is created. If no transport
    is provided, a default ``HTTPWebhookTransport`` with a no-op handler
    (always returns 200) is used.

    Args:
        registry: An existing ``WebhookRegistry`` to use (or ``None``).
        transport: An existing ``WebhookTransport`` to use (or ``None``).

    Returns:
        A configured ``WebhookDispatcher`` instance.
    """
    if registry is None:
        registry = create_webhook_registry()
    if transport is None:
        transport = HTTPWebhookTransport(
            handler=lambda url, payload, headers, timeout: (200, "OK")
        )
    return WebhookDispatcher(registry=registry, transport=transport)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    # Enums
    "WebhookEventType",
    "WebhookStatus",
    "SignatureAlgorithm",
    # Dataclasses
    "WebhookEvent",
    "WebhookConfig",
    "DeliveryResult",
    # Abstract base
    "WebhookTransport",
    # Concrete classes
    "HTTPWebhookTransport",
    "WebhookSignature",
    "WebhookRegistry",
    "WebhookDispatcher",
    # Factory functions
    "create_webhook_registry",
    "create_webhook_dispatcher",
]
