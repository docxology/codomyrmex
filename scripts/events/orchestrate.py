#!/usr/bin/env python3
"""
Events Module Orchestrator

Thin orchestrator script providing CLI access to events module functionality.
Calls actual module functions from codomyrmex.events.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
    )

# Import module functions
from codomyrmex.events import get_event_bus, publish_event

logger = get_logger(__name__)


def handle_publish(args):
    """Handle publish event command."""
    try:
        if getattr(args, "verbose", False):
            logger.info(f"Publishing event: {args.event_type}")

        event_bus = get_event_bus()
        result = publish_event(args.event_type, args.data if args.data else {})

        print_section("Event Publishing Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        print_success("Event published successfully")
        return True

    except Exception as e:
        logger.exception("Unexpected error publishing event")
        print_error("Unexpected error publishing event", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Events operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s publish --event-type test.event --data '{"key": "value"}'
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish an event")
    publish_parser.add_argument("--event-type", "-e", required=True, help="Event type")
    publish_parser.add_argument("--data", "-d", help="Event data (JSON)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "publish": handle_publish,
    }

    handler = handlers.get(args.command)
    if handler:
        success = handler(args)
        return 0 if success else 1
    else:
        print_error("Unknown command", context=args.command)
        return 1


if __name__ == "__main__":
    sys.exit(main())

