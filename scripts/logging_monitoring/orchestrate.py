#!/usr/bin/env python3
"""
Logging Monitoring Orchestrator

Thin orchestrator script providing CLI access to logging_monitoring module functionality.
Calls actual module functions from codomyrmex.logging_monitoring.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import LoggingError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        print_error,
        print_section,
        print_success,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        print_error,
        print_section,
        print_success,
    )

logger = get_logger(__name__)


def handle_test_logging(args):
    """Handle test logging command."""
    try:
        # Setup logging
        setup_logging()

        # Get logger
        test_logger = get_logger("test_logger")

        if getattr(args, "verbose", False):
            logger.info("Testing logging functionality")

        print_section("Testing logging levels")

        # Test different log levels
        test_logger.debug("This is a DEBUG message")
        test_logger.info("This is an INFO message")
        test_logger.warning("This is a WARNING message")
        test_logger.error("This is an ERROR message")
        test_logger.critical("This is a CRITICAL message")

        print_section("", separator="")
        print_success("Logging test completed")
        return True

    except LoggingError as e:
        logger.error(f"Logging error: {str(e)}")
        print_error("Logging error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during logging test")
        print_error("Unexpected error during logging test", exception=e)
        return False


def handle_info(args):
    """Handle info command."""
    try:
        print_section("Logging Monitoring Module Information")
        print("This module provides centralized logging facilities for Codomyrmex.")
        print("")
        print("Key Functions:")
        print("  - setup_logging(): Initialize logging system")
        print("  - get_logger(name): Get logger instance for a module")
        print("")
        print("Configuration:")
        print("  - Set CODOMYRMEX_LOG_LEVEL in .env file")
        print("  - Set CODOMYRMEX_LOG_FILE in .env file")
        print("  - Set CODOMYRMEX_LOG_FORMAT in .env file")
        print_section("", separator="")
        return True

    except Exception as e:
        logger.exception("Unexpected error showing info")
        print_error("Unexpected error showing info", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Logging Monitoring operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s test-logging
  %(prog)s info
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test logging command
    subparsers.add_parser("test-logging", help="Test logging functionality")

    # Info command
    subparsers.add_parser("info", help="Show module information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "test-logging": handle_test_logging,
        "info": handle_info,
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

