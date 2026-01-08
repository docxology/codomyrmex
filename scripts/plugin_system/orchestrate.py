#!/usr/bin/env python3
"""
Plugin System Module Orchestrator

Thin orchestrator script providing CLI access to plugin_system module functionality.
Calls actual module functions from codomyrmex.plugin_system.

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
        validate_file_path,
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
        validate_file_path,
    )

# Import module functions
from codomyrmex.plugin_system import PluginManager

logger = get_logger(__name__)


def handle_load(args):
    """Handle load plugin command."""
    try:
        plugin_path = validate_file_path(args.path, must_exist=True)

        if getattr(args, "verbose", False):
            logger.info(f"Loading plugin: {plugin_path}")

        manager = PluginManager()
        result = manager.load_plugin(str(plugin_path))

        print_section("Plugin Loading Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        print_success("Plugin loaded successfully")
        return True

    except Exception as e:
        logger.exception("Unexpected error loading plugin")
        print_error("Unexpected error loading plugin", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Plugin System operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s load --path plugin.py
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Load command
    load_parser = subparsers.add_parser("load", help="Load a plugin")
    load_parser.add_argument("--path", "-p", required=True, help="Plugin file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "load": handle_load,
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


