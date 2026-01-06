#!/usr/bin/env python3
"""
Agents Module Orchestrator

Thin orchestrator script providing CLI access to agents module functionality.
Calls actual module functions from codomyrmex.agents.

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
    sys.path.insert(0, str(Path(__file__).parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
    )

# Import module functions
from codomyrmex.agents import AgentInterface, get_config

logger = get_logger(__name__)


def handle_info(args):
    """Handle info command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Retrieving agents module information")

        config = get_config()
        info = {
            "module": "agents",
            "description": "Agent framework integrations",
            "config": config.__dict__ if hasattr(config, '__dict__') else {},
        }

        print_section("Agents Module Information")
        print(format_output(info, format_type="json"))
        print_section("", separator="")

        print_success("Information retrieved")
        return True

    except Exception as e:
        logger.exception("Unexpected error retrieving information")
        print_error("Unexpected error retrieving information", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Agents operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s info
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get agents module information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
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

