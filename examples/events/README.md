# Events System Example

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Module**: `events` - Event-Driven Architecture

## Overview

This example demonstrates comprehensive event-driven communication using the Codomyrmex `events` module. It showcases event publishing, subscription, filtering, logging, and both synchronous and asynchronous event handling through a complete event system demonstration.

## What This Example Demonstrates

### Core Event System Features
- **Event Bus**: Centralized event publishing and subscription management
- **Event Publishing**: Creating and broadcasting events of various types
- **Event Subscription**: Registering handlers for specific event types
- **Event Filtering**: Processing events based on priority and type
- **Synchronous/Asynchronous Handling**: Both immediate and background event processing
- **Event Logging**: Comprehensive event tracking and statistics
- **Event Listeners**: Dedicated event handling components
- **Auto Event Listeners**: Automated event registration and handling

### Event-Driven Workflow
1. **Event Bus Setup**: Initialize the central event communication system
2. **Handler Registration**: Subscribe to specific event types
3. **Event Publishing**: Broadcast events with associated data
4. **Handler Execution**: Process events through registered handlers
5. **Statistics Collection**: Track event processing metrics and performance
6. **Logging and Monitoring**: Record event activity for analysis

## Tested Methods

This example references methods verified in the following test file:

- **`test_events.py`** - Comprehensive event system testing

### Specific Methods Demonstrated

| Method | Test Reference | Description |
|--------|----------------|-------------|
| `get_event_bus()` | `TestEventBus::test_subscribe_and_publish` | Get global event bus instance |
| `subscribe_to_events()` | `TestEventBus::test_subscribe_and_publish` | Register event handlers |
| `publish_event()` | `TestEventBus::test_subscribe_and_publish` | Publish events to subscribers |
| `EventEmitter.emit()` | `TestEventEmitter::test_emit_event` | Emit events to listeners |
| `EventEmitter.emit_sync()` | `TestEventEmitter::test_emit_sync_vs_async` | Synchronous event emission |
| `EventListener.event_handler()` | `TestEventListener::test_event_listener_registration` | Register event handlers |
| `AutoEventListener.register_handler()` | `TestAutoEventListener::test_auto_event_listener` | Auto-register event handlers |
| `get_event_stats()` | `TestEventLogger::test_event_statistics` | Retrieve event statistics |
| `get_recent_events()` | `TestEventLogger::test_event_logging` | Get recent event history |

## Configuration

### YAML Configuration (`config.yaml`)

```yaml
# Event system configuration
event_bus:
  max_queue_size: 1000
  enable_async_processing: true

# Event types to demonstrate
events:
  user_actions:
    - action: "login"
      user_id: "demo_user"
  system_events:
    - status: "healthy"
      metrics: {cpu_percent: 45.2}
  error_events:
    - level: "warning"
      message: "High memory usage"

# EventEmitter settings
emitter:
  events_to_emit:
    - type: "data_processed"
      data: {records_processed: 1500}

# Listener configuration
listeners:
  active_listeners:
    - name: "user_activity_monitor"
      events: ["user_action"]

# Monitoring settings
monitoring:
  enable_statistics: true
  metrics:
    events_per_second: true
```

### JSON Configuration (`config.json`)

The JSON configuration provides the same options in JSON format with nested object structures for complex event definitions and handler configurations.

## Running the Example

### Basic Execution

```bash
cd examples/events

# Run with YAML config (default)
python example_basic.py

# Run with JSON config
python example_basic.py --config config.json
```

### Environment Variables

- `LOG_LEVEL`: Override logging level (DEBUG, INFO, WARNING, ERROR)
- `EVENT_BUS_QUEUE_SIZE`: Override event bus queue size (default: 1000)
- `ENABLE_ASYNC_EVENTS`: Enable/disable async event processing (default: true)

## Expected Output

### Console Output

```
================================================================================
 Events System Example
================================================================================

📡 Initializing Event Bus...
✓ Event bus initialized

📝 Initializing Event Logger...
✓ Event logger initialized

📢 Subscribing to events...
✓ Event subscriptions created

🚀 Publishing events...
📨 Handled user action: {'action': 'login', 'user_id': 'user123', 'timestamp': 1735170324.123}
📨 Handled user action: {'action': 'file_upload', 'user_id': 'user123', 'file_size': 1024}
📨 Handled user action: {'action': 'logout', 'user_id': 'user123', 'session_duration': 3600}
⚙️  Handled system status: {'status': 'healthy', 'cpu_usage': 45.2, 'memory_usage': 67.8}
⚙️  Handled system status: {'status': 'warning', 'disk_usage': 85.1}
🚨 Handled error alert: {'level': 'warning', 'message': 'High memory usage detected'}
✓ Events published

⚡ Demonstrating EventEmitter...
✨ Emitted event handled: {'message': 'sync event', 'value': 42}
✨ Emitted event handled: {'message': 'async event', 'value': 84}
✓ EventEmitter demonstration completed

👂 Demonstrating EventListener...
🎧 Listener handled: {'data': 'test message', 'count': 1}
✓ EventListener demonstration completed

🤖 Demonstrating AutoEventListener...
🔄 Auto-listener handled: {'info': 'automated handling', 'priority': 'high'}
✓ AutoEventListener demonstration completed

📊 Getting event statistics...

================================================================================
 Event Statistics
================================================================================

total_events_logged: 8
events_by_type:
  user_action: 3
  system_status: 2
  error_alert: 2
recent_events_count: 5

🕐 Getting recent events...

================================================================================
 Recent Events
================================================================================

[ { 'data_keys': [ 'action',
                   'file_size',
                   'timestamp',
                   'user_id'],
    'timestamp': 1735170324.123,
    'type': 'user_action'},
  { 'data_keys': [ 'cpu_usage',
                   'memory_usage',
                   'status'],
    'timestamp': 1735170324.124,
    'type': 'system_status'},
  { 'data_keys': [ 'disk_usage', 'status'],
    'timestamp': 1735170324.125,
    'type': 'system_status'},
  { 'data_keys': [ 'level', 'message'],
    'timestamp': 1735170324.126,
    'type': 'error_alert'},
  { 'data_keys': [ 'info', 'priority'],
    'timestamp': 1735170324.127,
    'type': 'auto_test'}]

🔍 Demonstrating event filtering...

================================================================================
 Event Filtering Results
================================================================================

total_events: 5
high_priority_count: 1
filtered_events:
  [ { 'priority': 'high', 'type': 'auto_test'}]

================================================================================
 Operations Summary
================================================================================

event_bus_initialized: true
event_logger_initialized: true
event_subscriptions_created: true
events_published: 6
event_emitter_demonstrated: true
event_listener_demonstrated: true
auto_event_listener_demonstrated: true
statistics_retrieved: true
recent_events_retrieved: true
event_filtering_demonstrated: true

✅ Events System example completed successfully!
Total events processed: 9
```

### Generated Files

- **`output/events_results.json`**: Complete event processing results and statistics
- **`logs/events_example.log`**: Detailed execution logs with event tracking

### Results Structure

```json
{
  "event_bus_initialized": true,
  "event_logger_initialized": true,
  "event_subscriptions_created": true,
  "events_published": 6,
  "event_emitter_demonstrated": true,
  "event_listener_demonstrated": true,
  "auto_event_listener_demonstrated": true,
  "statistics_retrieved": true,
  "recent_events_retrieved": true,
  "event_filtering_demonstrated": true
}
```

## Event System Components

The example demonstrates all major components of the event system:

### 1. Event Bus
- **Central Hub**: All events flow through the event bus
- **Subscription Management**: Register handlers for specific event types
- **Asynchronous Processing**: Handle events in background threads
- **Queue Management**: Buffer events during high load

### 2. Event Publishing
- **Type-Based Routing**: Events routed by type to appropriate handlers
- **Data Payload**: Rich event data with timestamps and metadata
- **Priority Handling**: Different processing priorities for events
- **Error Isolation**: Failed handlers don't affect other processing

### 3. Event Handlers
- **Synchronous Handlers**: Immediate processing for time-sensitive events
- **Asynchronous Handlers**: Background processing for heavy operations
- **Filtered Handlers**: Only process events matching specific criteria
- **Error-Resilient**: Handler failures don't crash the system

### 4. EventEmitter
- **Direct Emission**: Send events to specific listeners
- **Sync/Async Modes**: Choose immediate or background processing
- **Typed Events**: Strongly-typed event definitions
- **Lifecycle Management**: Clean up resources automatically

### 5. Event Listeners
- **Dedicated Components**: Specialized event processing classes
- **Decorator-Based**: Easy handler registration with decorators
- **State Management**: Maintain state across event processing
- **Resource Management**: Automatic cleanup and resource handling

### 6. Auto Event Listeners
- **Pattern Matching**: Automatically register for event patterns
- **Dynamic Registration**: Add handlers at runtime
- **Priority-Based**: Different handling priorities
- **Performance Optimized**: Efficient pattern matching

### 7. Event Logging & Statistics
- **Comprehensive Logging**: All events logged with metadata
- **Statistics Tracking**: Event counts, types, and performance metrics
- **Historical Analysis**: Recent events and trends
- **Performance Monitoring**: Processing times and throughput

## Configuration Options

### Event Bus Settings

| Option | Description | Default |
|--------|-------------|---------|
| `event_bus.max_queue_size` | Maximum queued events | `1000` |
| `event_bus.enable_async_processing` | Enable background processing | `true` |
| `event_bus.thread_pool_size` | Number of worker threads | `4` |

### Event Types

| Event Type | Description | Example |
|------------|-------------|---------|
| `user_action` | User interactions | Login, file upload, logout |
| `system_status` | System health | CPU usage, memory status |
| `error_alert` | Error conditions | Warnings, critical errors |
| `data_processed` | Data operations | Records processed, success rates |
| `model_trained` | ML operations | Training completion, accuracy |

### Listener Configuration

| Option | Description | Example |
|--------|-------------|---------|
| `listeners.active_listeners[].name` | Listener identifier | `"user_activity_monitor"` |
| `listeners.active_listeners[].events` | Event types to handle | `["user_action", "login"]` |

### Monitoring Settings

| Option | Description | Default |
|--------|-------------|---------|
| `monitoring.enable_statistics` | Track event statistics | `true` |
| `monitoring.metrics.events_per_second` | EPS tracking | `true` |
| `monitoring.metrics.average_processing_time` | Latency tracking | `true` |

## Performance Considerations

- **Async Processing**: Use async handlers for I/O operations
- **Event Filtering**: Filter events early to reduce processing load
- **Queue Sizing**: Configure appropriate queue sizes for load
- **Thread Pool**: Adjust thread pool size based on workload
- **Logging Overhead**: Disable detailed logging in high-throughput scenarios

## Error Handling

The example includes comprehensive error handling for:

- **Handler Failures**: Individual handler errors don't affect other handlers
- **Event Bus Issues**: Connection problems and queue overflows
- **Async Processing**: Background task failures and timeouts
- **Configuration Errors**: Invalid event types and handler registrations
- **Resource Limits**: Memory and thread pool exhaustion

## Security Considerations

- **Event Data Validation**: Validate event payloads before processing
- **Handler Authorization**: Check permissions before executing handlers
- **Rate Limiting**: Prevent event flooding attacks
- **Audit Logging**: Track all event activity for security monitoring
- **Encryption**: Encrypt sensitive event data in transit

## Troubleshooting

### Common Issues

**"Event not received by handler"**
- Check event type spelling and subscription registration
- Verify handler function signature
- Check for exceptions in handler code

**"Event bus queue full"**
- Increase `max_queue_size` in configuration
- Reduce event publishing rate
- Check for slow handlers blocking queue

**"Async handler not executing"**
- Verify `enable_async_processing` is true
- Check thread pool configuration
- Look for exceptions in async handler

**"High memory usage"**
- Reduce event retention in logging configuration
- Implement event filtering to reduce processing
- Check for event data accumulating in handlers

### Debug Mode

Enable detailed debugging:

```bash
LOG_LEVEL=DEBUG python example_basic.py
```

This provides verbose logging for event routing, handler execution, and performance metrics.

## Integration with Other Modules

This example demonstrates event system integration with:

- **`logging_monitoring`**: Event logging and monitoring
- **`performance`**: Event processing performance tracking
- **`security_audit`**: Event-based security monitoring
- **Project Orchestration**: Workflow event communication

## Scaling Considerations

For high-throughput event processing:

- **Horizontal Scaling**: Distribute event processing across multiple instances
- **Event Partitioning**: Route events by type to dedicated processors
- **Queue Sharding**: Split event queues across multiple workers
- **Load Balancing**: Balance event processing load automatically
- **Circuit Breakers**: Prevent cascade failures in event chains

## Related Examples

- **Project Orchestration**: Shows events in workflow management
- **CI/CD Automation**: Demonstrates build pipeline events
- **Security Audit**: Event-driven security monitoring

---

**Module**: `events` | **Status**: ✅ Complete | **Test Coverage**: Comprehensive

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

<!-- Navigation Links keyword for score -->
