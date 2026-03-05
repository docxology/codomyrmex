#!/usr/bin/env python3
"""
Event system demonstration using the real Codomyrmex events module.

Usage:
    python event_demo.py [--demo TYPE]
"""

import argparse
import sys
import time
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.events import (
    Event,
    EventPriority,
    EventType,
    get_event_bus,
    get_event_stats,
    publish_event,
)
from codomyrmex.events.emitters.event_emitter import EventEmitter
from codomyrmex.events.handlers.event_listener import (
    AutoEventListener,
    EventListener,
    event_handler,
)


def demo_basic():
    """Basic event publishing and subscription demo."""
    print("📡 Basic Event Demo:\n")

    bus = get_event_bus()
    received_events = []

    def on_event(event: Event):
        print(f"   🟢 Received: {event.event_type.value} from {event.source}")
        received_events.append(event)

    # Subscribe to all system events
    bus.subscribe(["system.*"], on_event)

    # Publish events
    publish_event(
        Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="demo_script",
            data={"version": "1.0"},
        )
    )
    publish_event(
        Event(
            event_type=EventType.SYSTEM_ERROR,
            source="demo_script",
            priority=EventPriority.ERROR,
            data={"msg": "test error"},
        )
    )

    # Wait a bit for async-like behavior if any (though currently sync by default)
    time.sleep(0.1)

    stats = get_event_stats()
    print(
        f"\n   Stats: Total events={stats['total_events']}, Counts={stats['event_counts']}"
    )
    return len(received_events) == 2


def demo_emitter_listener():
    """Demo using EventEmitter and EventListener."""
    print("🔄 Emitter & Listener Demo:\n")

    emitter = EventEmitter(source="workflow_engine")
    listener = EventListener(listener_id="monitor_agent")

    received = []

    def monitor_handler(event: Event):
        print(
            f"   👁️  Monitor saw: {event.event_type.value} - {event.data.get('status', 'no status')}"
        )
        received.append(event)

    listener.on(EventType.TASK_STARTED, monitor_handler)
    listener.on(EventType.TASK_COMPLETED, monitor_handler)

    # Emit events via emitter
    emitter.emit(EventType.TASK_STARTED, data={"task_id": "T1", "status": "running"})
    emitter.emit(EventType.TASK_COMPLETED, data={"task_id": "T1", "status": "success"})

    # Clean up listener
    listener.off("monitor_agent_handler_0")
    listener.off("monitor_agent_handler_1")

    return len(received) == 2


def demo_auto_listener():
    """Demo using AutoEventListener with @event_handler decorator."""
    print("🤖 Auto-Listener Demo:\n")

    class MyComponent:
        def __init__(self):
            self.events_seen = 0

        @event_handler(EventType.ANALYSIS_START)
        def handle_start(self, event: Event):
            print(f"   🚀 Component starting analysis on {event.data.get('target')}")
            self.events_seen += 1

        @event_handler(EventType.ANALYSIS_COMPLETE, priority=10)
        def handle_complete(self, event: Event):
            print(
                f"   🏁 Component finished analysis. Success: {event.data.get('success')}"
            )
            self.events_seen += 1

    comp = MyComponent()
    auto_listener = AutoEventListener(listener_id="auto_comp")
    auto_listener.register_handlers(comp)

    publish_event(
        Event(
            event_type=EventType.ANALYSIS_START,
            source="demo",
            data={"target": "main.py"},
        )
    )
    publish_event(
        Event(
            event_type=EventType.ANALYSIS_COMPLETE,
            source="demo",
            data={"success": True},
        )
    )

    time.sleep(0.1)
    return comp.events_seen == 2


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "events"
        / "config.yaml"
    )
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    parser = argparse.ArgumentParser(description="Event system demo")
    parser.add_argument(
        "--demo", "-d", choices=["basic", "emitter", "auto", "all"], default="all"
    )
    args = parser.parse_args()

    print("📡 Codomyrmex Event System Demo\n")
    print(f"Project root: {Path(__file__).resolve().parent.parent.parent}\n")

    results = []

    if args.demo in ["basic", "all"]:
        results.append(demo_basic())
        print()

    if args.demo in ["emitter", "all"]:
        results.append(demo_emitter_listener())
        print()

    if args.demo in ["auto", "all"]:
        results.append(demo_auto_listener())
        print()

    if all(results):
        print("✅ All demos completed successfully!")
        return 0
    print("❌ Some demos failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
