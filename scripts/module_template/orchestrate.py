#!/usr/bin/env python3
"""
Module Template Orchestrator

Thin orchestrator script providing CLI access to module_template functionality.
The module_template is a template for creating new modules, so this orchestrator
provides information about using the template.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
        save_json_file,
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
        save_json_file,
    )

logger = get_logger(__name__)


def handle_info(args):
    """Handle info command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Retrieving module template information")

        info = {
            "module": "module_template",
            "description": "Template for creating new Codomyrmex modules",
            "instructions": [
                "Copy the module_template directory",
                "Rename it to your module name",
                "Update the __init__.py and other files",
                "Follow the module structure guidelines",
            ],
            "location": "src/codomyrmex/module_template/",
        }

        print_section("Module Template Information")
        print("The module_template is a template for creating new Codomyrmex modules.")
        print("")
        print("To create a new module:")
        for i, instruction in enumerate(info["instructions"], 1):
            print(f"{i}. {instruction}")
        print("")
        print(f"See: {info['location']} for the template")
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(info, args.output)
            print_success(f"Information saved to {output_path}")

        return True

    except Exception as e:
        logger.exception("Unexpected error retrieving module template information")
        print_error("Unexpected error retrieving module template information", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Module Template operations",
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
    info_parser = subparsers.add_parser("info", help="Show module template information")
    info_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

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

