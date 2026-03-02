# events - Functional Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `events` module provides a high-performance, decoupled communication layer for the Codomyrmex ecosystem. It implements the Publish-Subscribe pattern with support for synchronous and asynchronous execution, structured payloads, and comprehensive observability.

## Design Principles

- **Loose Coupling**: Publishers and subscribers are completely unaware of each other.
- **Type Safety**: Events use the `EventType` enum and can be validated against JSON schemas.
- **Prioritized Delivery**: Subscribers can specify a priority level to control execution order.
- **Observability by Default**: Every event passing through the system is logged and indexed for real-time monitoring and historical analysis.

## Functional Requirements

1. **Routing**: Support for exact type matching and pattern-based (wildcard) matching.
2. **Filtering**: Subscribers can provide arbitrary filter functions to further narrow down relevant events.
3. **Concurrency**: Thread-safe implementation supporting both synchronous handlers and asynchronous (coroutine) handlers.
4. **Persistence**: An append-only `EventStore` for long-term storage and replaying of event streams.
5. **Validation**: Integration with `jsonschema` for validating event payloads.

## Interface Contracts

### Event
- `event_id`: UUID string.
- `event_type`: `EventType` enum or string.
- `source`: String identifying the origin.
- `timestamp`: Unix timestamp (float).
- `data`: Payload dictionary.
- `priority`: `EventPriority` enum or integer.

### EventBus
- `subscribe(patterns, handler, ...)` -> `subscriber_id`
- `unsubscribe(subscriber_id)` -> `bool`
- `publish(event)`
- `emit_typed(event)` (Validates event type)

### EventLogger
- `log_event(event, ...)`
- `get_events(event_type, ...)` -> `list[EventLogEntry]`
- `get_event_statistics()` -> `dict`

### EventStore
- `append(stream_event)` -> `sequence_number`
- `read(from_seq, to_seq)` -> `list[StreamEvent]`
- `read_by_topic(topic)` -> `list[StreamEvent]`

## Directory Structure

- `core/`: Fundamental bus, schema, and exception definitions.
- `emitters/`: Higher-level event emission helpers.
- `handlers/`: Event listening and logging implementations.
- `notification/`: Service for externalizing events (Email, Slack, Webhooks).
- `streaming/`: Real-time event streaming via SSE/WebSockets.
