#!/usr/bin/env python3
"""
Templating Module Orchestrator

Thin orchestrator script providing CLI access to templating module functionality.
Calls actual module functions from codomyrmex.templating.

See also: src/codomyrmex/cli.py for main CLI integration
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

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import CodomyrmexError

# Import shared utilities
from codomyrmex.utils.cli_helpers import (
    format_output,
    print_error,
    print_section,
    print_success,
)

# Import module functions
try:
    from codomyrmex.templating import TemplateEngine
except ImportError:
    TemplateEngine = None

logger = get_logger(__name__)


def handle_basic(args):
    """Handle basic operation command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Running basic templating operation")

        if TemplateEngine is None:
            print_error("Module templating not yet fully implemented")
            return False

        instance = TemplateEngine()
        result = {"status": "success", "module": "templating"}

        print_section("Templating Operation Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        print_success("Operation completed successfully")
        return True

    except Exception as e:
        logger.exception("Unexpected error in templating operation")
        print_error("Unexpected error in templating operation", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Templating operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s basic
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Basic command
    basic_parser = subparsers.add_parser("basic", help="Basic templating operation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "basic": handle_basic,
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