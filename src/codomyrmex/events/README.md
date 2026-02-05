# events

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Event-driven architecture module enabling decoupled, asynchronous communication between Codomyrmex components. Provides an `EventBus` for publish/subscribe messaging, an `AsyncEventEmitter` for async event dispatch, typed event schemas with priority levels, and an `EventLogger` for auditing event flow. Supports event filtering by type and priority, handler timeout management, and structured event statistics.

## Key Exports

### Core Classes
- **`Event`** -- Immutable event object with type, priority, payload, timestamp, and source metadata
- **`EventType`** -- Enum defining event categories (system, module, user, error, lifecycle, etc.)
- **`EventPriority`** -- Enum for event priority levels (low, normal, high, critical)
- **`EventSchema`** -- Defines the expected payload structure for a given event type
- **`EventBus`** -- Central message bus for synchronous publish/subscribe with topic-based routing
- **`AsyncEventEmitter`** -- Async-compatible event emitter for non-blocking event dispatch
- **`EventLogger`** -- Records event flow for debugging and audit, with statistics tracking

### Functions
- **`get_event_bus()`** -- Returns the singleton EventBus instance for the current process
- **`publish_event()`** -- Publishes an event to the global event bus
- **`subscribe_to_events()`** -- Registers a handler for a specific event type on the global bus
- **`unsubscribe_from_events()`** -- Removes a previously registered event handler
- **`get_event_logger()`** -- Returns the singleton EventLogger instance
- **`get_event_stats()`** -- Returns event statistics (counts by type, handler execution times, error rates)

### Exceptions
- **`EventError`** -- Base exception for all event system errors
- **`EventPublishError`** -- Raised when event publishing fails
- **`EventSubscriptionError`** -- Raised when subscribing or unsubscribing fails
- **`EventHandlerError`** -- Raised when an event handler throws during execution
- **`EventTimeoutError`** -- Raised when an event handler exceeds its timeout
- **`EventValidationError`** -- Raised when an event payload does not match its schema
- **`EventQueueError`** -- Raised when the event queue is full or in an invalid state
- **`EventDeliveryError`** -- Raised when event delivery to a subscriber fails

## Directory Contents

- `event_schema.py` -- Event, EventType, EventPriority, and EventSchema definitions
- `event_bus.py` -- EventBus implementation with publish/subscribe, singleton access, and global convenience functions
- `emitter.py` -- AsyncEventEmitter for async event dispatch
- `event_emitter.py` -- Additional event emitter implementations
- `event_listener.py` -- Event listener base classes and utilities
- `event_logger.py` -- EventLogger for audit trails and statistics
- `exceptions.py` -- Full exception hierarchy for event system errors

## Navigation

- **Full Documentation**: [docs/modules/events/](../../../docs/modules/events/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
