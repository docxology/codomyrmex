# Codomyrmex Agents — src/codomyrmex/events/core

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides the foundational event infrastructure for Codomyrmex: a central event bus with pub/sub routing, typed event schemas with JSON Schema validation, a mixin for easy event integration into any class, and a hierarchy of event-specific exceptions.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `event_bus.py` | `Subscription` | Dataclass binding a subscriber ID, glob-based event patterns, handler callable, optional filter function, and priority |
| `event_bus.py` | `EventBus` | Central event router with thread-safe subscribe/unsubscribe, sync and async publish, `ThreadPoolExecutor` for async handlers, dead letter queue, and metrics counters |
| `event_bus.py` | `get_event_bus()` | Module-level singleton accessor for the global `EventBus` instance |
| `event_bus.py` | `publish_event()` / `subscribe_to_events()` / `unsubscribe_from_events()` | Convenience functions delegating to the global singleton |
| `event_schema.py` | `EventPriority` | Enum: DEBUG, INFO, NORMAL, WARNING, ERROR, CRITICAL, MONITORING |
| `event_schema.py` | `EventType` | Enum with ~50 event types across system, module, plugin, analysis, build, deploy, monitoring, user, data, security, workflow, and scheduler domains |
| `event_schema.py` | `Event` | Core dataclass with event_type, source, event_id (auto UUID), timestamp, correlation_id, data dict, metadata dict, and priority; supports `to_dict()`, `to_json()`, `from_dict()`, `from_json()` |
| `event_schema.py` | `EventSchema` | JSON Schema validator using `jsonschema` library; pre-loads schemas for standard event types (startup, module_load, analysis, build, error, metric, alert) |
| `event_schema.py` | `create_*_event()` | Seven factory functions for common events: system_startup, module_load, analysis_start, analysis_complete, error, metric, alert |
| `mixins.py` | `EventMixin` | Mixin class providing `init_events()`, `emit()`, `on()`, `off()`, and `cleanup_events()` for any module to gain event capabilities without managing the bus directly |
| `exceptions.py` | `EventPublishError`, `EventSubscriptionError`, `EventHandlerError`, `EventTimeoutError`, `EventValidationError`, `EventQueueError`, `EventDeliveryError` | Seven exception types inheriting from `codomyrmex.exceptions.EventError`, each with domain-specific context fields |

## Operating Contracts

- `Subscription.matches_event()` uses `fnmatch` glob matching on event type strings, enabling wildcard patterns like `"analysis.*"`.
- `EventBus` is thread-safe via `threading.RLock`; subscriber IDs are auto-generated if not provided.
- Failed handler invocations increment `events_failed` and log errors but do not propagate exceptions to the publisher.
- Events that fail all processing are placed in `dead_letter_queue`.
- `EventBus.publish()` auto-injects correlation IDs from `logging_monitoring.core.correlation.get_correlation_id()` when not set.
- `EventSchema.validate_event()` permits events without a registered schema (returns `(True, [])` by default).
- All exceptions store context in a `self.context` dict inherited from `EventError`.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging, correlation IDs), `codomyrmex.exceptions` (`EventError` base), `jsonschema` (external)
- **Used by**: `events.emitters`, `events.handlers`, and any module using `EventMixin` or the `publish_event()` / `subscribe_to_events()` functions

## Navigation

- **Parent**: [events](../README.md)
- **Root**: [Codomyrmex](../../../../../README.md)
