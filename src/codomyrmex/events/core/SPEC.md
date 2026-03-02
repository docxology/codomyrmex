# Events Core — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides the central event bus, typed event schemas with JSON Schema validation, convenience factory functions for common events, an event mixin for easy integration, and a hierarchy of domain-specific exceptions for the Codomyrmex event system.

## Architecture

Pub/sub pattern with glob-based topic matching (`fnmatch`). The `EventBus` maintains a thread-safe subscription registry and dispatches synchronously by default, with optional async mode using `asyncio.Queue` and `ThreadPoolExecutor`. A module-level singleton (`get_event_bus()`) provides a shared global bus. `EventSchema` validates event payloads against registered JSON Schemas using `jsonschema`.

## Key Classes

### `EventBus`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `max_workers: int = 4`, `enable_async: bool = False` | `None` | Initialize with thread pool and optional async queue |
| `subscribe` | `event_patterns: list[Any]`, `handler: Callable`, `subscriber_id: str \| None`, `filter_func`, `priority: int` | `str` | Register handler for matching patterns; returns subscriber ID |
| `subscribe_typed` | `event_type: EventType`, `handler`, `subscriber_id`, `**kwargs` | `str` | Convenience wrapper for single EventType subscription |
| `unsubscribe` | `subscriber_id: str` | `bool` | Remove a subscription |
| `publish` | `event: Event` | `None` | Publish event synchronously (or queue if async enabled) |
| `publish_async` | `event: Event` | `None` | Publish via async queue |
| `emit_typed` | `event: Event` | `None` | Publish with EventType validation (raises TypeError) |
| `get_stats` | — | `dict[str, Any]` | Return publish/process/fail counters and subscriber info |
| `shutdown` | — | `None` | Shut down executor and clear subscriptions |

### `Event`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `to_dict` | — | `dict[str, Any]` | Serialize to dictionary |
| `to_json` | — | `str` | Serialize to JSON string |
| `from_dict` | `data: dict` | `Event` | Class method: deserialize from dict |
| `from_json` | `json_str: str` | `Event` | Class method: deserialize from JSON |

### `EventSchema`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `validate_event` | `event: Event` | `tuple[bool, list[str]]` | Validate event data against registered schema |
| `register_event_schema` | `event_type: EventType`, `schema: dict` | `None` | Register JSON Schema for an event type |
| `get_event_schema` | `event_type: EventType` | `dict \| None` | Retrieve registered schema |
| `list_registered_schemas` | — | `list[str]` | List all registered event type names |

### `EventMixin`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `init_events` | `source: str`, `event_bus: EventBus \| None` | `None` | Initialize event capabilities |
| `emit` | `event_type`, `data`, `correlation_id`, `priority`, `metadata` | `Event` | Emit an event from this module |
| `on` | `event_types: list`, `handler`, `priority: int` | `str` | Subscribe to events; returns subscription ID |
| `off` | `subscription_id: str` | `bool` | Unsubscribe |
| `cleanup_events` | — | `None` | Unsubscribe from all registered subscriptions |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring` (logger, correlation IDs), `codomyrmex.exceptions` (`EventError`)
- **External**: `jsonschema` (JSON Schema validation)

## Constraints

- `EventBus` global singleton is lazily initialized; call `get_event_bus()` to access.
- Subscription matching uses `fnmatch.fnmatch` on string-coerced event type values.
- Handler exceptions are caught (ValueError, RuntimeError, AttributeError, OSError, TypeError) and logged but not re-raised.
- Pre-loaded schemas cover 12 standard event types; unknown types pass validation by default.
- The `dead_letter_queue` is an unbounded in-memory list; no automatic eviction.

## Error Handling

- `EventPublishError` — event publishing failure (includes event_type, event_id, channel in context)
- `EventSubscriptionError` — subscription management failure (includes subscriber_id, reason)
- `EventHandlerError` — handler execution failure (includes handler_name, original_error)
- `EventTimeoutError` — processing timeout (includes timeout_seconds, processing_stage)
- `EventValidationError` — schema validation failure (includes validation_errors list)
- `EventQueueError` — queue operation failure (includes queue_name, queue_size, max_size)
- `EventDeliveryError` — delivery failure (includes failed_subscribers, retry_count)
