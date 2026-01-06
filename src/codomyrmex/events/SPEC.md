# events - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Provides an asynchronous event bus for decoupling system components. Implements the Publish-Subscribe pattern.

## Design Principles
- **Decoupling**: Publishers need not know subscribers.
- **Typed Payloads**: Events carry structured data (dicts/pydantic models).

## Functional Requirements
1.  **Publishing**: `bus.publish(event)` or `emitter.emit(type, data)`
2.  **Subscription**: `bus.subscribe(types, handler)` or `listener.on(type, handler)`
3.  **Synchronous Emission**: `emitter.emit_sync(type, data)` for immediate processing

## Interface Contracts
- **Event**: Dataclass with `event_id`, `event_type`, `source`, `timestamp`, and `priority`.
- **Event Bus**: Central routing hub with support for async queues and thread pools.
- **Event Priority**: Supports `DEBUG`, `INFO`, `NORMAL`, `WARNING`, `ERROR`, `CRITICAL`.

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)
