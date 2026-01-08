#!/usr/bin/env python3
"""
Terminal Interface Orchestrator

Thin orchestrator script providing CLI access to terminal_interface module functionality.
Calls actual module functions from codomyrmex.terminal_interface.

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
from codomyrmex.exceptions import TerminalError, InteractiveShellError, CodomyrmexError

# Import shared utilities
from codomyrmex.utils.cli_helpers import (
    format_output,
    print_error,
    print_info,
    print_section,
    print_success,
)

# Import module functions
from codomyrmex.terminal_interface import InteractiveShell, TerminalFormatter

logger = get_logger(__name__)


def handle_shell(args):
    """Handle interactive shell command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Starting interactive shell")

        shell = InteractiveShell()
        shell.run()
        print_success("Interactive shell session completed")
        return True

    except InteractiveShellError as e:
        logger.error(f"Interactive shell error: {str(e)}")
        print_error("Interactive shell error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except TerminalError as e:
        logger.error(f"Terminal error: {str(e)}")
        print_error("Terminal error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error starting interactive shell")
        print_error("Unexpected error starting interactive shell", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def handle_format(args):
    """Handle terminal formatting test command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Testing terminal formatting")

        formatter = TerminalFormatter()

        print_section("Terminal Formatting Test")
        print(formatter.header("Test Header", "=", 60))
        print(formatter.success("Success message"))
        print(formatter.error("Error message"))
        print(formatter.warning("Warning message"))
        print(formatter.color("Colored text", "BRIGHT_CYAN"))
        print_section("", separator="")

        print_success("Terminal formatting test completed")
        return True

    except TerminalError as e:
        logger.error(f"Terminal error: {str(e)}")
        print_error("Terminal error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error testing terminal formatting")
        print_error("Unexpected error testing terminal formatting", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Terminal Interface operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s shell
  %(prog)s format
  %(prog)s shell --verbose
  %(prog)s format --verbose
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Shell command
    subparsers.add_parser("shell", help="Launch interactive shell")

    # Format command
    subparsers.add_parser("format", help="Test terminal formatting")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "shell": handle_shell,
        "format": handle_format,
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
