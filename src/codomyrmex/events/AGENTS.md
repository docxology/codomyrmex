# Codomyrmex Agents — src/codomyrmex/events

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Events Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Event system module providing asynchronous event handling and communication capabilities for the Codomyrmex platform. This module implements a publish-subscribe pattern for decoupling components and enabling reactive programming patterns across the platform.

The events module serves as the foundation for event-driven architecture, allowing modules to communicate through typed events without direct dependencies.

## Module Overview

### Key Capabilities
- **Event Publishing**: Emit events with typed payloads
- **Event Subscription**: Register listeners for specific event types
- **Event Bus**: Centralized event routing and delivery
- **Event Logging**: Comprehensive event tracking and debugging

### Key Features
- Type-safe event definitions with schemas
- Asynchronous event processing
- Event filtering and routing capabilities
- Performance monitoring and metrics

## Function Signatures

### Event Bus Functions

```python
def get_event_bus() -> EventBus
```

Get the global event bus instance.

**Returns:** `EventBus` - Global event bus instance

```python
def publish_event(event: Event) -> None
```

Publish an event to the event bus for processing.

**Parameters:**
- `event` (Event): Event object to publish

**Returns:** None

```python
def subscribe_to_events(event_types: List[EventType], handler: Callable[[Event], Any], subscriber_id: Optional[str] = None, priority: int = 0) -> str
```

Subscribe to multiple event types with a handler.

**Parameters:**
- `event_types` (List[EventType]): List of event types to subscribe to
- `handler` (Callable[[Event], Any]): Function to handle events
- `subscriber_id` (Optional[str]): Unique subscriber identifier
- `priority` (int): Handler priority (higher numbers execute first)

**Returns:** `str` - Subscriber ID for unsubscription

```python
def unsubscribe_from_events(subscriber_id: str) -> bool
```

Unsubscribe from events using subscriber ID.

**Parameters:**
- `subscriber_id` (str): Subscriber ID to remove

**Returns:** `bool` - True if successfully unsubscribed, False otherwise

### Event Emitter Functions

```python
def create_emitter(source: str) -> EventEmitter
```

Create a new event emitter for a specific source.

**Parameters:**
- `source` (str): Source identifier for emitted events

**Returns:** `EventEmitter` - New event emitter instance

```python
def emit_event(event_type: EventType, source: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> None
```

Emit an event with the specified type and data.

**Parameters:**
- `event_type` (EventType): Type of event to emit
- `source` (str): Source identifier for the event
- `data` (Optional[Dict[str, Any]]): Event data payload
- `**kwargs` - Additional event data

**Returns:** None

### Event Listener Functions

```python
def event_handler(event_types: Union[EventType, List[EventType]], priority: int = 0)
```

Decorator to register event handler methods.

**Parameters:**
- `event_types` (Union[EventType, List[EventType]]): Event types to handle
- `priority` (int): Handler priority

**Returns:** Decorator function

```python
def create_listener(listener_id: str) -> EventListener
```

Create a new event listener with specified ID.

**Parameters:**
- `listener_id` (str): Unique identifier for the listener

**Returns:** `EventListener` - New event listener instance

```python
def create_auto_listener(listener_id: str, obj: Any) -> AutoEventListener
```

Create an auto-discovering event listener for an object.

**Parameters:**
- `listener_id` (str): Unique identifier for the listener
- `obj` (Any): Object to scan for event handler methods

**Returns:** `AutoEventListener` - New auto-discovering listener

### Event Logging Functions

```python
def get_event_logger() -> EventLogger
```

Get the global event logger instance.

**Returns:** `EventLogger` - Global event logger instance

```python
def log_event_to_monitoring(event: Event, handler_count: int = 0, processing_time: float = 0.0) -> None
```

Log event processing information to monitoring system.

**Parameters:**
- `event` (Event): Event that was processed
- `handler_count` (int): Number of handlers that processed the event
- `processing_time` (float): Time taken to process the event

**Returns:** None

```python
def get_event_stats() -> Dict[str, Any]
```

Get statistics about event processing.

**Returns:** `Dict[str, Any]` - Event processing statistics

```python
def get_recent_events(limit: int = 50) -> List[EventLogEntry]
```

Get recent event log entries.

**Parameters:**
- `limit` (int): Maximum number of entries to return. Defaults to 50

**Returns:** `List[EventLogEntry]` - Recent event log entries

```python
def export_event_logs(filepath: str, format: str = 'json') -> None
```

Export event logs to a file.

**Parameters:**
- `filepath` (str): Path to export file
- `format` (str): Export format ('json', 'csv', 'txt'). Defaults to 'json'

**Returns:** None

```python
def generate_performance_report() -> Dict[str, Any]
```

Generate performance report for event system.

**Returns:** `Dict[str, Any]` - Performance metrics and analysis

### Event Schema Functions

```python
def create_system_startup_event(version: str, components: List[str]) -> Event
```

Create a system startup event.

**Parameters:**
- `version` (str): System version
- `components` (List[str]): List of loaded components

**Returns:** `Event` - System startup event

```python
def create_module_load_event(module_name: str, version: str, load_time: float) -> Event
```

Create a module load event.

**Parameters:**
- `module_name` (str): Name of the loaded module
- `version` (str): Module version
- `load_time` (float): Time taken to load the module

**Returns:** `Event` - Module load event

```python
def create_analysis_start_event(analysis_type: str, target: str, parameters: Optional[Dict[str, Any]] = None) -> Event
```

Create an analysis start event.

**Parameters:**
- `analysis_type` (str): Type of analysis starting
- `target` (str): Analysis target
- `parameters` (Optional[Dict[str, Any]]): Analysis parameters

**Returns:** `Event` - Analysis start event

```python
def create_analysis_complete_event(analysis_type: str, target: str, results: Dict[str, Any], duration: float, success: bool) -> Event
```

Create an analysis complete event.

**Parameters:**
- `analysis_type` (str): Type of analysis completed
- `target` (str): Analysis target
- `results` (Dict[str, Any]): Analysis results
- `duration` (float): Analysis duration
- `success` (bool): Whether analysis was successful

**Returns:** `Event` - Analysis complete event

```python
def create_error_event(event_type: EventType, source: str, error_message: str, error_type: str = "unknown", context: Optional[Dict[str, Any]] = None) -> Event
```

Create an error event.

**Parameters:**
- `event_type` (EventType): Type of error event
- `source` (str): Error source
- `error_message` (str): Error message
- `error_type` (str): Type of error. Defaults to "unknown"
- `context` (Optional[Dict[str, Any]]): Additional error context

**Returns:** `Event` - Error event

```python
def create_metric_event(metric_name: str, value: Union[int, float, str, bool], metric_type: str = "gauge", labels: Optional[Dict[str, str]] = None) -> Event
```

Create a metric event.

**Parameters:**
- `metric_name` (str): Name of the metric
- `value` (Union[int, float, str, bool]): Metric value
- `metric_type` (str): Type of metric. Defaults to "gauge"
- `labels` (Optional[Dict[str, str]]): Metric labels

**Returns:** `Event` - Metric event

```python
def create_alert_event(alert_name: str, level: str, message: str, threshold: Any = None, current_value: Any = None) -> Event
```

Create an alert event.

**Parameters:**
- `alert_name` (str): Name of the alert
- `level` (str): Alert severity level
- `message` (str): Alert message
- `threshold` (Any): Alert threshold value
- `current_value` (Any): Current measured value

**Returns:** `Event` - Alert event

## Data Structures

### EventPriority Enum
```python
class EventPriority(Enum):
    DEBUG = "debug"
    INFO = "info"
    NORMAL = "normal"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

Enumeration of event priority levels.

### EventType Enum
```python
class EventType(Enum):
    SYSTEM_STARTUP = "system.startup"
    MODULE_LOAD = "module.load"
    ANALYSIS_START = "analysis.start"
    ANALYSIS_PROGRESS = "analysis.progress"
    ANALYSIS_COMPLETE = "analysis.complete"
    ANALYSIS_ERROR = "analysis.error"
    ERROR_OCCURRED = "error.occurred"
```

Enumeration of standard event types in the platform.

### Event Class
```python
@dataclass
class Event:
    event_type: EventType
    source: str
    timestamp: datetime
    priority: EventPriority = EventPriority.NORMAL
    data: Dict[str, Any] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = None
```

Core event data structure with type, source, and payload information.

### EventSchema Class
```python
@dataclass
class EventSchema:
    event_type: EventType
    required_fields: List[str]
    optional_fields: List[str]
    field_types: Dict[str, str]
    validation_rules: Dict[str, Any]
```

Schema definition for validating event structures.

### EventEmitter Class
```python
class EventEmitter:
    def __init__(self, source: str): ...

    def emit(self, event_type: EventType, data: Optional[Dict[str, Any]] = None, **kwargs) -> None: ...

    def emit_sync(self, event_type: EventType, data: Optional[Dict[str, Any]] = None, **kwargs) -> None: ...

    def emit_async(self, event_type: EventType, data: Optional[Dict[str, Any]] = None, **kwargs) -> Awaitable[None]: ...
```

Class for emitting events with source tracking and metrics.

### EventListener Class
```python
class EventListener:
    def __init__(self, listener_id: str): ...

    def on(self, event_types: Union[EventType, List[EventType]], handler: Callable[[Event], Any], priority: int = 0) -> str: ...

    def off(self, subscription_id: str) -> bool: ...

    def once(self, event_type: EventType, handler: Callable[[Event], Any], priority: int = 0) -> str: ...
```

Base class for event listeners with subscription management.

### AutoEventListener Class
```python
class AutoEventListener(EventListener):
    def __init__(self, listener_id: str, obj: Any): ...

    def _discover_handlers(self, obj: Any) -> Dict[str, Callable]: ...

    def _register_handlers(self) -> None: ...
```

Event listener that automatically discovers handler methods on objects.

### EventLogEntry Class
```python
@dataclass
class EventLogEntry:
    event: Event
    handler_count: int
    processing_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
```

Log entry for event processing tracking.

### EventLogger Class
```python
class EventLogger:
    def __init__(self): ...

    def log_event(self, event: Event, handler_count: int = 0, processing_time: float = 0.0) -> None: ...

    def get_recent_events(self, limit: int = 50) -> List[EventLogEntry]: ...

    def get_event_stats(self) -> Dict[str, Any]: ...

    def export_logs(self, filepath: str, format: str = 'json') -> None: ...

    def generate_performance_report(self) -> Dict[str, Any]: ...
```

Class for logging and monitoring event system performance.

### Subscription Class
```python
@dataclass
class Subscription:
    subscription_id: str
    event_types: List[EventType]
    handler: Callable[[Event], Any]
    priority: int
    created_at: datetime
```

Subscription information for event handling.

### EventBus Class
```python
class EventBus:
    def __init__(self): ...

    def publish(self, event: Event) -> None: ...

    def subscribe(self, event_types: List[EventType], handler: Callable[[Event], Any], subscriber_id: Optional[str] = None, priority: int = 0) -> str: ...

    def unsubscribe(self, subscription_id: str) -> bool: ...

    def get_subscriptions(self) -> Dict[str, Subscription]: ...

    def get_stats(self) -> Dict[str, Any]: ...
```

Central event bus for routing events to subscribers.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `event_bus.py` – Central event routing and management
- `event_emitter.py` – Event publishing utilities
- `event_listener.py` – Event subscription management
- `event_logger.py` – Event tracking and debugging
- `event_schema.py` – Event type definitions and validation

## Operating Contracts

### Universal Event Protocols

All event handling within the Codomyrmex platform must:

1. **Type Safety** - Use defined event schemas for payload validation
2. **Error Isolation** - Event handler failures don't affect other listeners
3. **Performance Monitoring** - Track event processing metrics
4. **Security Validation** - Validate event sources and payloads

### Module-Specific Guidelines

#### Event Publishing
- Use descriptive event type names with namespace prefixes
- Include sufficient context in event payloads
- Handle publishing failures gracefully
- Consider event frequency and performance impact

#### Event Listening
- Register listeners at appropriate initialization points
- Handle exceptions within listener callbacks
- Unregister listeners when no longer needed
- Consider listener execution order and dependencies

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation