# Codomyrmex Agents — src/codomyrmex/events

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Event-Driven Architecture for Codomyrmex. Provides an asynchronous event bus for decoupling system components, implementing the Publish-Subscribe pattern with support for synchronous and asynchronous event handling, filtering, prioritization, and event logging.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `event_bus.py` – Central event bus for managing event routing and subscriptions
- `event_emitter.py` – Event emitter for components that want to publish events
- `event_listener.py` – Event listener for components that want to receive events
- `event_logger.py` – Event logging and monitoring
- `event_schema.py` – Event schema definitions and types

## Key Classes and Functions

### EventBus (`event_bus.py`)
- `EventBus(max_workers: int = 4, enable_async: bool = True)` – Initialize event bus with worker threads
- `subscribe(event_types: List[EventType], handler: Callable[[Event], Any], subscriber_id: Optional[str] = None, filter_func: Optional[Callable[[Event], bool]] = None, priority: int = 0) -> str` – Subscribe to events
- `unsubscribe(subscriber_id: str) -> bool` – Unsubscribe from events
- `publish(event: Event) -> None` – Publish an event to all subscribers
- `get_stats() -> dict` – Get event bus statistics

### Event (`event_schema.py`)
- `Event` (dataclass) – Represents an event in the system:
  - `event_type: EventType` – Type of event
  - `source: str` – Source identifier
  - `event_id: str` – Unique event identifier
  - `timestamp: float` – Event timestamp
  - `correlation_id: Optional[str]` – Correlation ID for tracing
  - `data: Dict[str, Any]` – Event data payload
  - `metadata: Dict[str, Any]` – Additional metadata
  - `priority: Union[int, EventPriority]` – Event priority
- `to_dict() -> Dict[str, Any]` – Convert event to dictionary
- `to_json() -> str` – Convert event to JSON string
- `from_dict(data: Dict[str, Any]) -> Event` – Create event from dictionary
- `from_json(json_str: str) -> Event` – Create event from JSON string

### EventType (`event_schema.py`)
- `EventType` (Enum) – Standard event types including:
  - System events: SYSTEM_STARTUP, SYSTEM_SHUTDOWN, SYSTEM_ERROR, SYSTEM_CONFIG_CHANGE
  - Module events: MODULE_LOAD, MODULE_UNLOAD, MODULE_ERROR, MODULE_CONFIG_UPDATE
  - Plugin events: PLUGIN_LOAD, PLUGIN_UNLOAD, PLUGIN_EXECUTE, PLUGIN_ERROR
  - Analysis events: ANALYSIS_START, ANALYSIS_PROGRESS, ANALYSIS_COMPLETE, ANALYSIS_ERROR
  - Build events: BUILD_START, BUILD_PROGRESS, BUILD_COMPLETE, BUILD_ERROR
  - Deployment events: DEPLOY_START, DEPLOY_PROGRESS, DEPLOY_COMPLETE, DEPLOY_ERROR, DEPLOY_ROLLBACK
  - Monitoring events: METRIC_UPDATE, ALERT_TRIGGERED, HEALTH_CHECK, PERFORMANCE_DEGRADATION
  - User events: USER_ACTION, USER_LOGIN, USER_LOGOUT, USER_ERROR
  - Data events: DATA_RECEIVED, DATA_PROCESSED, DATA_STORED, DATA_ERROR
  - Security events: SECURITY_VIOLATION, SECURITY_SCAN_COMPLETE, SECURITY_ALERT
  - Custom events: CUSTOM

### EventPriority (`event_schema.py`)
- `EventPriority` (Enum) – Event priority levels: DEBUG, INFO, NORMAL, WARNING, ERROR, CRITICAL

### EventEmitter (`event_emitter.py`)
- `EventEmitter(source: str, event_bus: Optional[EventBus] = None)` – Initialize event emitter
- `emit(event_type: EventType, data: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, priority: int = 0) -> None` – Emit a single event asynchronously
- `emit_sync(event_type: EventType, data: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, priority: int = 0) -> None` – Emit a single event synchronously
- `emit_batch(events: List[Event]) -> None` – Emit multiple events

### EventListener (`event_listener.py`)
- `EventListener(listener_id: str, event_bus: Optional[EventBus] = None)` – Initialize event listener
- `on(event_types: Union[EventType, List[EventType]], handler: Callable[[Event], Any], handler_name: Optional[str] = None, filter_func: Optional[Callable[[Event], bool]] = None, priority: int = 0) -> str` – Register an event handler
- `off(handler_name: str) -> bool` – Unregister an event handler
- `clear() -> None` – Clear all handlers

### Module Functions (`__init__.py`)
- `get_event_bus() -> EventBus` – Get the global event bus instance
- `publish_event(event: Event) -> None` – Publish an event to the global event bus
- `subscribe_to_events(event_types: List[EventType], handler: Callable[[Event], Any], subscriber_id: Optional[str] = None, filter_func: Optional[Callable[[Event], bool]] = None, priority: int = 0) -> str` – Subscribe to events on the global event bus
- `unsubscribe_from_events(subscriber_id: str) -> bool` – Unsubscribe from events
- `get_event_logger() -> EventLogger` – Get the global event logger instance
- `log_event_to_monitoring(event: Event) -> None` – Log event to monitoring system
- `get_event_stats() -> dict` – Get event statistics
- `get_recent_events(limit: int = 100) -> List[Event]` – Get recent events
- `export_event_logs(format: str = "json") -> str` – Export event logs
- `generate_performance_report() -> dict` – Generate performance report

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation