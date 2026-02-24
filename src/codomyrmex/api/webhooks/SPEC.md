# Technical Specification - Webhooks

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.api.webhooks`  
**Last Updated**: 2026-01-29

## 1. Purpose

Webhook dispatch and receipt management for event-driven APIs

## 2. Architecture

### 2.1 Components

```
webhooks/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `api`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.api.webhooks
from codomyrmex.api.webhooks import (
    # Enums
    WebhookEventType,        # Enum: CREATED, UPDATED, DELETED, CUSTOM
    WebhookStatus,           # Enum: PENDING, DELIVERED, FAILED, RETRYING
    SignatureAlgorithm,      # Enum: HMAC_SHA256, HMAC_SHA512
    # Dataclasses
    WebhookEvent,            # Event payload with event_type, payload, event_id, timestamp, source
    WebhookConfig,           # Endpoint config: url, secret, events, max_retries, retry_delay, timeout
    DeliveryResult,          # Delivery attempt result: webhook_id, event_id, status, status_code, attempt
    # Abstract base
    WebhookTransport,        # ABC for sending webhook payloads (implement .send())
    # Concrete classes
    HTTPWebhookTransport,    # Callback-based transport for testing and in-process dispatch
    WebhookSignature,        # Static HMAC sign() and verify() utilities
    WebhookRegistry,         # In-memory registry for webhook configs (register/unregister/list)
    WebhookDispatcher,       # Dispatches events to registered endpoints with optional retry
    # Factory functions
    create_webhook_registry, # Returns new empty WebhookRegistry
    create_webhook_dispatcher, # Returns WebhookDispatcher with optional defaults
)

# Key class signatures:
class WebhookRegistry:
    def register(self, webhook_id: str, config: WebhookConfig) -> None: ...
    def unregister(self, webhook_id: str) -> None: ...
    def get(self, webhook_id: str) -> WebhookConfig | None: ...
    def list_all(self) -> dict[str, WebhookConfig]: ...
    def list_for_event(self, event_type: WebhookEventType) -> dict[str, WebhookConfig]: ...

class WebhookDispatcher:
    def dispatch(self, event: WebhookEvent) -> list[DeliveryResult]: ...
    def dispatch_with_retry(self, event: WebhookEvent, max_retries: int | None = None) -> list[DeliveryResult]: ...

class WebhookSignature:
    @staticmethod
    def sign(payload: str, secret: str, algorithm: SignatureAlgorithm = ...) -> str: ...
    @staticmethod
    def verify(payload: str, secret: str, signature: str, algorithm: SignatureAlgorithm = ...) -> bool: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Single-file implementation**: All types, transport, registry, and dispatcher live in `__init__.py` to keep the module self-contained with zero internal imports beyond stdlib.
2. **Abstract transport layer**: `WebhookTransport` ABC decouples delivery mechanism from dispatch logic, allowing test-friendly callback transports without network I/O.
3. **HMAC signing with constant-time comparison**: `WebhookSignature.verify` uses `hmac.compare_digest` to prevent timing attacks on signature verification.

### 4.2 Limitations

- `HTTPWebhookTransport` is callback-based and does not perform real HTTP requests; a real HTTP transport must be implemented for production use
- Retry logic in `dispatch_with_retry` uses synchronous `time.sleep`; not suitable for async/event-loop contexts
- In-memory registry only; no persistence across process restarts

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/api/webhooks/
```

## 6. Future Considerations

- Async transport implementation using `httpx` or `aiohttp` for non-blocking delivery
- Persistent delivery log (database-backed) for audit and replay of failed deliveries
- Exponential backoff with jitter in `dispatch_with_retry` (currently uses linear delay)
