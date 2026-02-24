# Personal AI Infrastructure -- Events Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Events module provides a publish/subscribe (pub/sub) event bus for decoupled, event-driven communication between codomyrmex modules. It sits in the Foundation Layer as cross-cutting infrastructure, enabling any module to emit structured events and any other module to react without direct import dependencies. The bus supports both synchronous and asynchronous handlers, glob-pattern subscriptions, priority-based dispatch, correlation ID propagation, dead-letter queuing, and JSON Schema validation of event payloads.

## PAI Capabilities

### Event Bus

The `EventBus` is the central routing component. It manages subscriptions, matches events to handlers via glob patterns, and dispatches in priority order. A global singleton is available via `get_event_bus()`, and modules can also instantiate private buses for isolation.

```python
from codomyrmex.events import EventBus, Event, EventType

bus = EventBus(max_workers=4, enable_async=False)

# Subscribe to events using glob patterns
def on_build(event: Event):
    print(f"Build event: {event.data}")

bus.subscribe(
    event_patterns=["build.*"],
    handler=on_build,
    subscriber_id="build_watcher",
    priority=10,
)

# Emit a typed event
event = Event(
    event_type=EventType.BUILD_START,
    source="ci_pipeline",
    data={"build_type": "release", "target": "codomyrmex"},
)
bus.publish(event)

# Use the EventMixin for cleaner integration
from codomyrmex.events import EventMixin

class CodeAnalyzer(EventMixin):
    def __init__(self):
        self.init_events("code_analyzer")

    def analyze(self, path: str):
        self.emit(EventType.ANALYSIS_START, {"target": path})
        # ... perform analysis ...
        self.emit(EventType.ANALYSIS_COMPLETE, {"target": path, "success": True})
```

### Typed Event Definitions

The `EventType` enum and `EventSchema` validator enforce structure across the system:

- **50+ predefined event types** organized by domain: system, module, plugin, analysis, build, deploy, monitoring, security, workflow, scheduler, and user interaction
- **JSON Schema validation** via `EventSchema.validate_event()` ensures payloads conform to declared shapes before dispatch
- **Custom schemas** can be registered per event type with `EventSchema.register_event_schema()`
- **Convenience constructors** like `create_analysis_start_event()`, `create_error_event()`, and `create_metric_event()` produce valid, pre-structured events
- **Serialization** support via `Event.to_dict()`, `Event.to_json()`, `Event.from_dict()`, and `Event.from_json()` for persistence and transport
- **Priority levels** defined in `EventPriority`: DEBUG, INFO, NORMAL, WARNING, ERROR, CRITICAL, MONITORING

### Async Event Support

The module provides full async capabilities for non-blocking event workflows:

- **`AsyncEventEmitter`** wraps the bus for `await`-based publishing and supports delayed emission via `emit_later(event_type, payload, delay)`
- **`AsyncStream`** provides backpressure-aware streaming with per-subscriber buffers, dispatcher loop, and async iterator consumption via `async for event in stream.consume(sub_id)`
- **`BatchingStream`** accumulates events and flushes in configurable batches (by count or time interval) for high-throughput scenarios
- **`WebSocketStream`** wraps `AsyncStream` for real-time browser delivery
- **Async handlers** are auto-detected by `inspect.iscoroutinefunction()` and dispatched via the thread pool executor

```python
from codomyrmex.events import AsyncEventEmitter, EventType

emitter = AsyncEventEmitter()

# Immediate async emit
await emitter.emit(EventType.TASK_COMPLETED, {"task_id": "t-42"})

# Delayed emit (fires after 5 seconds)
emitter.emit_later(EventType.ALERT_TRIGGERED, {"alert_name": "memory_high"}, delay=5.0)
```

## MCP Tools

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `emit_event` | Emit a named event with payload, source, and priority to the event bus | READ-ONLY |
| `list_event_types` | List all registered event types and their subscriber counts | READ-ONLY |
| `get_event_history` | Retrieve recent event history, optionally filtered by event type | READ-ONLY |

All three tools are safe operations that do not modify files, execute commands, or alter system state beyond the in-memory event bus. They are available without Trust Gateway elevation.

### MCP Tool Usage Examples

```python
# Via MCP bridge -- emit an event
emit_event(
    event_type="task.completed",
    payload={"task_id": "build-77", "duration_ms": 1230},
    source="orchestrator",
    priority="normal",
)
# Returns: {"status": "success", "event_type": "task.completed", "source": "orchestrator"}

# Via MCP bridge -- list registered types
list_event_types()
# Returns: {"status": "success", "event_types": [...], "count": 52}

# Via MCP bridge -- query history
get_event_history(event_type="build.*", limit=10)
# Returns: {"status": "success", "events": [...], "count": 10}
```

## PAI Algorithm Phase Mapping

| Phase | Events Contribution |
|-------|---------------------|
| **OBSERVE** | Subscribe to system and module events to detect state changes; query event history to understand recent activity and context before acting |
| **THINK** | Analyze event patterns and frequency to identify bottlenecks, recurring errors, or anomalous behavior; use correlation IDs to trace causal chains |
| **PLAN** | Define event-driven workflow triggers and subscribe to gate events that signal when preconditions are met before proceeding |
| **BUILD** | Emit `build.start`, `build.progress`, and `build.complete` events so other modules can react to artifact creation in real time |
| **EXECUTE** | Emit and consume events during workflow execution; use the event bus for inter-agent coordination without tight coupling |
| **VERIFY** | Emit `security.scan_complete` and `analysis.complete` events; subscribe to `task.failed` and `workflow.failed` for automated retry or escalation |
| **LEARN** | Event history provides a structured audit trail; replay events for post-mortem analysis; aggregate metrics via `metric.update` events |

## PAI Configuration

### Environment Variables

```bash
# Event bus worker pool size (default: 4)
export CODOMYRMEX_EVENT_WORKERS=4

# Enable async event processing (default: false)
export CODOMYRMEX_EVENT_ASYNC=false

# Event history retention limit (default: 1000)
export CODOMYRMEX_EVENT_HISTORY_LIMIT=1000

# Dead letter queue max size (default: 100)
export CODOMYRMEX_EVENT_DLQ_MAX=100
```

### Programmatic Configuration

```python
from codomyrmex.events import EventBus

# High-throughput async bus
bus = EventBus(max_workers=8, enable_async=True)

# Register custom schema for domain events
from codomyrmex.events import EventSchema, EventType

schema = EventSchema()
schema.register_event_schema(EventType.CUSTOM, {
    "type": "object",
    "properties": {
        "action": {"type": "string"},
        "target": {"type": "string"},
    },
    "required": ["action"],
})
```

## PAI Best Practices

### 1. Use Typed Events Over Raw Strings

Prefer `EventType` enum values and `emit_typed()` for compile-time safety. Raw string event types bypass schema validation and make refactoring harder.

```python
# Preferred -- typed, validated
bus.emit_typed(Event(event_type=EventType.BUILD_START, source="ci", data={...}))

# Avoid -- untyped, no validation
bus.publish(Event(event_type="build.start", source="ci", data={...}))
```

### 2. Propagate Correlation IDs

The bus auto-injects correlation IDs from the logging context when `correlation_id` is `None`. Always let this propagation happen rather than generating your own IDs, so that events can be traced end-to-end through the PAI Algorithm phases.

### 3. Use EventMixin for Module Integration

Any module that needs to emit or consume events should inherit from `EventMixin` rather than managing the bus directly. The mixin handles lazy initialization, source tagging, subscription tracking, and cleanup.

```python
from codomyrmex.events import EventMixin, EventType

class SecurityScanner(EventMixin):
    def __init__(self):
        self.init_events("security_scanner")
        self.on([EventType.BUILD_COMPLETE], self._on_build_complete)

    def _on_build_complete(self, event):
        # Auto-trigger security scan after every build
        self.emit(EventType.ANALYSIS_START, {
            "analysis_type": "security_scan",
            "target": event.data.get("target", "unknown"),
        })

    def __del__(self):
        self.cleanup_events()
```

### 4. Integrate With the Orchestrator via Events

The orchestrator subscribes to workflow and task events. Emit `WORKFLOW_STARTED`, `TASK_COMPLETED`, and `TASK_FAILED` events from your workflows so the orchestrator can track progress, trigger retries, and update the PAI dashboard without polling.

### 5. Monitor the Dead Letter Queue

Events that fail all handler attempts land in `bus.dead_letter_queue`. Periodically inspect this list via `bus.get_stats()` to detect handler bugs or schema mismatches before they silently drop important signals.

## Architecture Role

**Foundation Layer** -- The events module has minimal dependencies: `logging_monitoring` (for structured logging and correlation IDs) and `jsonschema` (for payload validation). It is consumed by: `orchestrator/` (workflow lifecycle events), `agents/` (inter-agent coordination), `git_operations/` (commit and branch events), `security/` (scan result events), `telemetry/` (metric aggregation), and the PAI dashboard (real-time streaming via `AsyncStream` and `WebSocketStream`).

### Sub-module Map

| Sub-module | Purpose |
|------------|---------|
| `core/event_bus.py` | Central `EventBus` class, subscription management, sync/async dispatch |
| `core/event_schema.py` | `Event` dataclass, `EventType` enum, `EventSchema` JSON validation |
| `core/mixins.py` | `EventMixin` for module integration |
| `core/exceptions.py` | Typed exception hierarchy for event operations |
| `emitters/emitter.py` | `AsyncEventEmitter` for non-blocking publishing |
| `streaming/async_stream.py` | `AsyncStream`, `WebSocketStream`, `BatchingStream` |
| `handlers/event_logger.py` | `EventLogger` for structured event logging |
| `mcp_tools.py` | Three MCP tools: `emit_event`, `list_event_types`, `get_event_history` |

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
