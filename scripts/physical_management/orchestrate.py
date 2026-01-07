#!/usr/bin/env python3
"""
Physical Management Orchestrator

Thin orchestrator script providing CLI access to physical_management module functionality.
Calls actual module functions from codomyrmex.physical_management.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import PhysicalManagementError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        save_json_file,
    )
except ImportError:
    # Fallback if running from different directory
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        save_json_file,
    )

logger = get_logger(__name__)


def handle_info(args):
    """Handle info command."""
    try:
        verbose = getattr(args, "verbose", False)
        if verbose:
            logger.info("Retrieving Physical Management module information")

        info = {
            "module": "physical_management",
            "description": "Physical object management, simulation, and sensor integration",
            "components": [
                {"name": "PhysicalObjectManager", "description": "Object lifecycle management"},
                {"name": "PhysicsSimulator", "description": "Physics simulation"},
                {"name": "SensorManager", "description": "Sensor integration"},
                {"name": "StreamingAnalytics", "description": "Real-time analytics"},
            ],
            "api_location": "src/codomyrmex/physical_management/",
        }

        print_section("Physical Management Module Information")
        print("This module provides physical object management, simulation, and sensor integration.")
        print("")
        print("Available Components:")
        for component in info["components"]:
            print(f"  - {component['name']}: {component['description']}")
        print("")
        print(f"See: {info['api_location']} for complete API")
        print_section("", separator="")

        output = getattr(args, "output", None)
        if output:
            output_path = save_json_file(info, output)
            if verbose:
                logger.info(f"Information saved to {output_path}")
            print_success(f"Information saved to {output_path}")

        return True

    except PhysicalManagementError as e:
        logger.error(f"Physical management error: {str(e)}")
        print_error("Failed to retrieve module information", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except CodomyrmexError as e:
        logger.error(f"Codomyrmex error: {str(e)}")
        print_error("Failed to retrieve module information", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error retrieving module information")
        print_error("Unexpected error retrieving module information", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Physical Management operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s info
  %(prog)s info --output info.json --verbose
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--output", "-o", help="Output file path for JSON results"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show module information")
    info_parser.add_argument("--output", "-o", help="Output file path for JSON results")

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
        print_error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

