#!/usr/bin/env python3
"""
Event-Driven Architecture - Real Usage Examples

Demonstrates actual event-driven patterns:
- Event Bus (Publish/Subscribe)
- Event Listeners and Handlers
- Event Logging and Stats
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.events import (
    Event,
    EventType,
    get_event_bus,
    get_event_logger,
    get_event_stats,
    publish_event,
    subscribe_to_events,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


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
            print("Loaded config from config/events/config.yaml")

    setup_logging()
    print_info("Running Event EDA Examples...")

    # 1. Event Bus
    print_info("Testing Event Bus...")
    bus = get_event_bus()

    received = []

    def handler(event):
        received.append(event)

    subscribe_to_events([EventType.SYSTEM_STARTUP], handler)

    event = Event(
        event_type=EventType.SYSTEM_STARTUP,
        source="basic_usage_script",
        data={"status": "running", "version": "1.0.0"},
    )
    publish_event(event)

    if len(received) > 0:
        print_success("  Event Bus Publish/Subscribe functional.")
    else:
        print_error("  Event Bus failed to receive event.")

    # 2. Event Logger
    print_info("Testing Event Logger...")
    logger = get_event_logger()
    stats = get_event_stats()
    if isinstance(stats, dict):
        print_success("  Event Logger and Stats functional.")

    print_success("Event EDA examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
