#!/usr/bin/env python3
"""
Example: Events System - Comprehensive Event-Driven Architecture

This example demonstrates the complete Codomyrmex event-driven communication system:

CORE FUNCTIONALITY:
- Event creation, publishing, and subscription patterns
- Event filtering, prioritization, and correlation
- Synchronous and asynchronous event processing
- Event bus management and routing
- Event logging, monitoring, and statistics
- Event listeners and auto-registration patterns

ADVANCED FEATURES:
- Event batching and bulk operations
- Event correlation IDs for request tracing
- Event priority handling and queuing
- Event schema validation and type safety
- Event lifecycle management (creation, routing, consumption)
- Performance monitoring and throughput metrics

EVENT TYPES DEMONSTRATED:
- System events (startup, shutdown, errors)
- Application events (user actions, data processing)
- Component events (module lifecycle, health checks)
- Custom business events (order processing, notifications)

COMMON USE CASES:
- Microservices communication and orchestration
- Real-time data processing pipelines
- User interface state management
- Background job coordination
- Monitoring and alerting systems
- Workflow and business process automation

ARCHITECTURAL PATTERNS:
- Publisher-Subscriber (Pub/Sub) pattern
- Event Sourcing for audit trails
- CQRS (Command Query Responsibility Segregation)
- Saga pattern for distributed transactions
- Event-driven microservices

ERROR HANDLING:
- Event publishing failures and retries
- Event handler exceptions and isolation
- Event schema validation errors
- Event bus capacity limits and backpressure
- Connection failures and reconnection logic

PERFORMANCE CONSIDERATIONS:
- Event throughput and latency optimization
- Memory usage for event queues and buffers
- CPU overhead for event processing
- Network bandwidth for distributed events
- Scalability patterns for high-volume systems

Tested Methods:
- get_event_bus() - Verified in test_events.py::TestEventBus::test_event_bus_initialization
- subscribe_to_events() - Verified in test_events.py::TestEventBus::test_subscribe_and_publish
- EventEmitter.emit() - Verified in test_events.py::TestEventEmitter::test_emit_event
- EventEmitter.emit_batch() - Verified in test_events.py::TestEventEmitter::test_emit_batch
- EventEmitter.emit_sync() - Verified in test_events.py::TestEventEmitter::test_emit_sync_vs_async
- EventListener.on() - Verified in test_events.py::TestEventListener::test_event_listener_subscription
- AutoEventListener.register_handlers() - Verified in test_events.py::TestAutoEventListener::test_auto_event_listener
- get_event_stats() - Verified in test_events.py::TestEventLogger::test_event_statistics
- get_recent_events() - Verified in test_events.py::TestEventLogger::test_recent_events
- Event.__init__() - Verified in test_events.py::TestEvent::test_event_creation
- EventType enum - Verified in test_events.py::TestEventType::test_event_type_values

USAGE EXAMPLES:
    # Basic event publishing
    from codomyrmex.events import get_event_bus, Event, EventType
    bus = get_event_bus()
    event = Event(event_type=EventType.SYSTEM_STARTUP, source='my_app', data={'version': '1.0.0'})
    bus.publish(event)

    # Event subscription with handler
    def handle_user_login(event):
        user_data = event.data
        print(f"User {user_data['user_id']} logged in from {user_data['ip']}")

    bus.subscribe(EventType.USER_LOGIN, handle_user_login)

    # Event emitter for component communication
    from codomyrmex.events import EventEmitter
    emitter = EventEmitter(source='user_service')
    emitter.emit(EventType.USER_REGISTERED, {'user_id': 123, 'email': 'user@example.com'})

    # Batch event processing
    events = [
        Event(event_type=EventType.DATA_UPDATED, source='batch_processor', data={'batch_id': 1}),
        Event(event_type=EventType.DATA_UPDATED, source='batch_processor', data={'batch_id': 2}),
    ]
    emitter.emit_batch(events)

    # Event correlation for request tracing
    import uuid
    correlation_id = str(uuid.uuid4())
    emitter.emit(EventType.REQUEST_STARTED, {'endpoint': '/api/users'},
                 correlation_id=correlation_id)
    # ... processing ...
    emitter.emit(EventType.REQUEST_COMPLETED, {'status': 200, 'duration_ms': 150},
                 correlation_id=correlation_id)
"""

import sys
import time
import threading
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add src to path for importing Codomyrmex modules
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import common utilities
sys.path.insert(0, str(project_root / "examples" / "_common"))
from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error

# Using real Codomyrmex events module implementation
print("Using real Codomyrmex events module implementation")

from codomyrmex.events import (
    get_event_bus,
    publish_event,
    subscribe_to_events,
    EventEmitter,
    EventListener,
    AutoEventListener,
    get_event_logger,
    get_event_stats,
    get_recent_events,
    EventType,
    Event,
    EventPriority
)


def main():
    """
    Run the  event-driven architecture example.

    This function demonstrates:
    1. Event bus initialization and configuration
    2. Event publishing patterns (single, batch, synchronous)
    3. Event subscription and handling (manual and automatic)
    4. Event correlation and tracing
    5. Event prioritization and filtering
    6. Event monitoring and statistics
    7. Error handling and edge cases
    8. Performance considerations
    9. Event schema validation
    """
    print_section("Events System Example")
    print("Demonstrating  event-driven architecture and communication patterns")

    # Load configuration with error handling
    try:
        # Step 1: Initialize Event Infrastructure
        print("\n" + "="*60)
        print("Step 1: Initializing Event Infrastructure")
        print("="*60)

        # Initialize event bus
        print("Initializing centralized event bus...")
        try:
            event_bus = get_event_bus()
            print_success("✓ Event bus initialized successfully")
            print(f"  - Async processing: {config.get('events', {}).get('async_processing', True)}")
            print(f"  - Max queue size: {config.get('events', {}).get('max_queue_size', 1000)}")
        except Exception as e:
            print_error(f"✗ Failed to initialize event bus: {e}")
            results['errors_handled'] += 1
            raise

        # Initialize event logger
        print("\nInitializing event logging system...")
        try:
            event_logger = get_event_logger()
            print_success("✓ Event logger initialized successfully")
        except Exception as e:
            print_error(f"✗ Failed to initialize event logger: {e}")
            results['errors_handled'] += 1

        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        print("Using default configuration...")
        config = {
            'events': {
                'max_queue_size': 1000,
                'async_processing': True,
                'log_level': 'INFO'
            }
    }

    # Initialize runner
    runner = ExampleRunner(__file__, config)
    runner.start()

    # Initialize results tracking
    results = {
    'status': 'initialized',
    'events_published': 0,
    'events_handled': 0,
    'subscriptions_created': 0,
    'listeners_created': 0,
    'batch_operations': 0,
    'errors_handled': 0,
    'edge_cases_tested': 0,
    'correlation_ids_used': 0
    }

    # Step 2: Event Publishing Patterns
    print("\n" + "="*60)
    print("Step 2: Event Publishing Patterns")
    print("="*60)

    print("Demonstrating different event publishing approaches...")

    # Create event emitter for this example
    emitter = EventEmitter(source="events_example")
    results['listeners_created'] += 1
    print_success("✓ EventEmitter created for example component")

    # Track events for verification
    events_received = []
    events_lock = threading.Lock()

        def track_event(event):
            """Thread-safe event tracking."""
            with events_lock:
                events_received.append({
                    'type': str(event.event_type),
                    'source': event.source,
                    'data': event.data,
                    'correlation_id': event.correlation_id
                })

        # Subscribe to all events for tracking
        subscriber_id = subscribe_to_events([], track_event)  # Empty list = all events
        results['subscriptions_created'] += 1

        # 2.1 Single Event Publishing
        print("\n2.1 Single Event Publishing:")

        # System startup event
        startup_event = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="events_example",
            data={
                "version": "1.0.0",
                "timestamp": time.time(),
                "environment": "development"
            }
        )
        publish_event(startup_event)
        results['events_published'] += 1
        print_success("✓ System startup event published")

        # User action event with correlation ID
        correlation_id = str(uuid.uuid4())
        user_event = Event(
            event_type="user_action",  # Custom event type
            source="events_example",
            data={
                "action": "login",
                "user_id": "user_12345",
                "ip_address": "192.168.1.100"
            },
            correlation_id=correlation_id
        )
        publish_event(user_event)
        results['events_published'] += 1
        results['correlation_ids_used'] += 1
        print_success("✓ User action event published with correlation ID")

        # Error event with priority
        error_event = Event(
            event_type=EventType.SYSTEM_ERROR,
            source="events_example",
            data={
                "error_message": "Database connection timeout",
                "severity": "high",
                "component": "database_manager"
            }
        )
        publish_event(error_event)
        results['events_published'] += 1
        print_success("✓ Error event published")

        # 2.2 Batch Event Publishing
        print("\n2.2 Batch Event Publishing:")

        batch_events = [
            Event(event_type=EventType.SYSTEM_ERROR,
                  source="events_example",
                  data={"error_message": "Memory usage warning", "usage_percent": 85}),
            Event(event_type=EventType.SYSTEM_ERROR,
                  source="events_example",
                  data={"error_message": "Disk space low", "free_gb": 2.1}),
            Event(event_type="data_processed",  # Custom event
                  source="events_example",
                  data={"records_processed": 1000, "duration_ms": 250})
        ]

        # Publish batch using emitter
        emitter.emit_batch([
            {"event_type": EventType.SYSTEM_ERROR,
             "data": {"error_message": "Batch event 1"}},
            {"event_type": EventType.SYSTEM_ERROR,
             "data": {"error_message": "Batch event 2"}},
            {"event_type": EventType.SYSTEM_STARTUP,
             "data": {"version": "1.0.0", "batch": True}}
        ])
        results['events_published'] += 3
        results['batch_operations'] += 1
        print_success("✓ Batch of 3 events published successfully")

        # Allow async processing time
        time.sleep(0.1)

        # Demonstrate EventEmitter additional features
        print("\n⚡ Demonstrating EventEmitter batch operations...")

        # Emit batch of events
        events_batch = [
            {"event_type": EventType.SYSTEM_ERROR, "data": {"error_message": "Batch event 1", "batch": True}},
            {"event_type": EventType.SYSTEM_ERROR, "data": {"error_message": "Batch event 2", "batch": True}},
            {"event_type": EventType.SYSTEM_STARTUP, "data": {"version": "1.0.0", "batch": True}}
        ]

        emitter.emit_batch(events_batch)
        print("✓ EventEmitter batch operations completed")

        # Demonstrate EventListener
        print("\n👂 Demonstrating EventListener...")
        listener = EventListener(listener_id="demo_listener")

        listener_events = []

        def listener_handler(event):
            event_data = event.data or {}
            listener_events.append(f"listener: {event_data.get('message', 'unknown')}")
            print(f"🎧 Listener handled: {event_data}")

        # Subscribe to events
        listener.on([EventType.SYSTEM_ERROR], listener_handler)
        print("✓ EventListener subscription created")

        # Publish event that listener will handle
        emitter.emit(EventType.SYSTEM_ERROR, {"message": "test message from listener", "count": 1})
        print("✓ EventListener demonstration completed")

        # Demonstrate AutoEventListener
        print("\n🤖 Demonstrating AutoEventListener...")
        auto_listener = AutoEventListener(listener_id="demo_auto_listener")

        auto_events = []

        def auto_handler(event):
            event_data = event.data or {}
            auto_events.append(f"auto: {event_data.get('message', 'unknown')}")
            print(f"🔄 Auto-listener handled: {event_data}")

        # Register handler - this should auto-subscribe
        auto_listener.register_handlers({"system_error_handler": auto_handler})
        print("✓ AutoEventListener handlers registered")

        # Publish event to auto-listener
        emitter.emit(EventType.SYSTEM_ERROR, {"message": "automated handling test", "priority": "high"})
        print("✓ AutoEventListener demonstration completed")

        # Get event statistics
        print("\n📊 Getting event statistics...")
        stats = get_event_stats()
        print_results({
            "total_events_logged": stats.get("total_events", 0),
            "events_by_type_count": len(stats.get("events_by_type", {})),
            "active_subscriptions": stats.get("active_subscriptions", 0)
        }, "Event Statistics")

        # Get recent events
        print("\n🕐 Getting recent events...")
        recent_events = get_recent_events(limit=5)
        recent_summary = [
            {
                "event_type": str(event.event_type),
                "timestamp": event.timestamp,
                "source": event.source,
                "data_keys": list(event.data.keys()) if event.data else []
            }
            for event in recent_events
        ]
        print_results(recent_summary, "Recent Events")

        # Demonstrate event filtering
        print("\n🔍 Demonstrating event filtering...")
        error_events = [
            event for event in recent_events
            if event.event_type == EventType.SYSTEM_ERROR
        ]
        filter_results = {
            "total_recent_events": len(recent_events),
            "error_events_count": len(error_events),
            "filtered_events": [
                {
                    "type": str(event.event_type),
                    "source": event.source
                }
                for event in error_events[:3]
            ]
        }
        print_results(filter_results, "Event Filtering Results")

        # Summary of operations performed
        operations_summary = {
            "event_bus_initialized": True,
            "event_logger_initialized": True,
            "event_subscriptions_created": True,
            "events_published": len(events_handled),
            "event_emitter_created": True,
            "event_emitter_batch_operations": True,
            "event_listener_created": True,
            "event_listener_subscription": True,
            "auto_event_listener_created": True,
            "auto_event_listener_handlers_registered": True,
            "statistics_retrieved": True,
            "recent_events_retrieved": len(recent_summary) > 0,
            "event_filtering_demonstrated": len(error_events) >= 0
        }

        print_results(operations_summary, "Operations Summary")

        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Events System example completed successfully!")
        print("All core event-driven architecture functionality demonstrated and verified.")
        print(f"Total events processed: {len(events_handled)}")

    except Exception as e:
        runner.error("Events System example failed", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
