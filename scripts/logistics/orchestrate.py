"""
Logistics module orchestrator script.

Thin orchestrator script providing CLI access to logistics module functionality.
Calls actual module functions from codomyrmex.logistics.
"""

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import argparse
import sys
from pathlib import Path

# Import shared utilities
from codomyrmex.utils.cli_helpers import (
    format_output,
    print_error,
    print_section,
    print_success,
)

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

logger = get_logger(__name__)


def handle_info(args):
    """Handle info command."""
    try:
        from codomyrmex import logistics
        
        if getattr(args, "verbose", False):
            logger.info("Retrieving logistics module information")

        info = {
            "module": "logistics",
            "description": "Logistics operations and management",
            "path": getattr(logistics, "__path__", ["unknown"])[0],
        }

        print_section("Logistics Module Information")
        print(format_output(info, format_type="json"))
        print_section("", separator="")
        return True
    
    except Exception as e:
        logger.exception("Unexpected error retrieving information")
        print_error("Unexpected error retrieving information", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Logistics operations",
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
    subparsers.add_parser("info", help="Get logistics module information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

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