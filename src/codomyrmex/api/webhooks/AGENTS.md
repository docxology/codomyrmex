# AI Agent Guidelines — api/webhooks

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides webhook dispatch and receipt management for event-driven APIs, including endpoint registration, HMAC payload signing, event dispatching with retry logic, and pluggable transport layers.

## Key Components

| Component | File | Role |
|-----------|------|------|
| `WebhookEventType` | `models.py` | Enum: `CREATED`, `UPDATED`, `DELETED`, `CUSTOM` |
| `WebhookStatus` | `models.py` | Enum: `PENDING`, `DELIVERED`, `FAILED`, `RETRYING` |
| `SignatureAlgorithm` | `models.py` | Enum: `HMAC_SHA256`, `HMAC_SHA512` |
| `WebhookEvent` | `models.py` | Dataclass with `event_type`, `payload`, auto-generated `event_id` (UUID4), `timestamp`, `source`; serializes via `to_dict()` / `to_json()` |
| `WebhookConfig` | `models.py` | Dataclass with `url`, `secret`, `events`, `max_retries`, `retry_delay`, `timeout`, `signature_algorithm`, `active` |
| `DeliveryResult` | `models.py` | Dataclass recording delivery outcome: `webhook_id`, `event_id`, `status`, `status_code`, `attempt`, `error` |
| `WebhookTransport` | `transport.py` | ABC requiring `send(url, payload, headers, timeout) -> (status_code, body)` |
| `HTTPWebhookTransport` | `transport.py` | Callback-based transport delegating to a user-supplied callable (for testing/in-process dispatch) |
| `WebhookSignature` | `signature.py` | Static utility: `sign(payload, secret, algorithm)` and `verify(payload, secret, signature, algorithm)` using HMAC with constant-time comparison |
| `WebhookRegistry` | `registry.py` | In-memory registry: `register`, `unregister`, `get`, `list_all`, `list_for_event` (filters by active + subscribed event type) |
| `WebhookDispatcher` | `dispatcher.py` | Dispatches events to matching webhooks; `dispatch` (single attempt) and `dispatch_with_retry` (linear backoff) |
| `create_webhook_registry` | `factory.py` | Factory returning empty `WebhookRegistry` |
| `create_webhook_dispatcher` | `factory.py` | Factory returning `WebhookDispatcher` with optional defaults (no-op transport if none provided) |

## Operating Contracts

- Register webhooks via `registry.register(webhook_id, config)` before dispatching events.
- `dispatcher.dispatch(event)` sends to all active webhooks subscribed to the event type.
- `dispatcher.dispatch_with_retry(event)` retries failed deliveries up to `config.max_retries` with `config.retry_delay` linear backoff.
- All payloads are HMAC-signed; `WebhookSignature.verify` uses `hmac.compare_digest` (constant-time) to prevent timing attacks.
- `list_for_event` returns webhooks that are active AND either subscribe to the specific event type or have an empty events list (wildcard).

## Integration Points

- **Parent**: `api` module re-exports webhook components via `api/webhooks/__init__.py`.
- **Transport**: Implement `WebhookTransport` ABC for production HTTP delivery (e.g., `httpx`, `aiohttp`).
- **Events module**: Can be paired with `codomyrmex.events` for internal event bus bridging.

## Navigation

- **Parent**: [api/README.md](../README.md)
- **Sibling**: [SPEC.md](SPEC.md) | [README.md](README.md)
- **Root**: [../../../../README.md](../../../../README.md)
