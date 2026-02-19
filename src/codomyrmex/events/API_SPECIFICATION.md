# Events Module API Specification

**Version**: v0.1.7 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview
The `events` module enables decoupled, asynchronous communication across the platform via a robust publish-subscribe system. It includes schema validation, prioritization, and persistent logging.

## 2. Core Components

### 2.1 Event Bus
- **`EventBus`**: Central message broker.
- **`publish_event`**: Broadcast a message.
- **`subscribe_to_events`**: Register a listener callback.

### 2.2 Structures
- **`Event`**: The message payload.
- **`EventSchema`**: Definition for validating event data.
- **`EventType` (Enum)**: Classification of events.
- **`EventPriority` (IntEnum)**: Urgency level.

### 2.3 Listeners
- **`EventListener`**: Base class for subscribers.
- **`AutoEventListener`**: Automatically subscribes based on decorators.

## 3. Usage Example

```python
from codomyrmex.events import publish_event, Event, EventType

event = Event(
    type=EventType.SYSTEM_INFO,
    source="my_module",
    data={"status": "online"}
)
publish_event(event)
```
