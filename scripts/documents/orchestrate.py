#!/usr/bin/env python3
"""
Documents Module Orchestrator

Thin orchestrator script providing CLI access to documents module functionality.
Calls actual module functions from codomyrmex.documents.

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
    validate_file_path,
)

# Import module functions - use available functions
try:
    from codomyrmex.documents import read_document, write_document, CORE_AVAILABLE
    if not CORE_AVAILABLE:
        raise ImportError("Core documents functions not available")
except ImportError:
    # Fallback: provide a simple info command only
    read_document = None
    write_document = None

logger = get_logger(__name__)


def handle_read(args):
    """Handle document reading command."""
    if not read_document:
        print_error("Document reading not available - core module failed to import")
        return False
    try:
        file_path = validate_file_path(args.file, must_exist=True, must_be_file=True)

        if getattr(args, "verbose", False):
            logger.info(f"Reading document: {file_path}")

        result = read_document(str(file_path))

        print_section("Document Contents")
        print(format_output({"content": result[:500] + "..." if len(str(result)) > 500 else result}, format_type="json"))
        print_section("", separator="")

        print_success("Document read successfully")
        return True

    except Exception as e:
        logger.exception("Unexpected error reading document")
        print_error("Unexpected error reading document", exception=e)
        return False


def handle_info(args):
    """Handle info command."""
    info = {
        "module": "documents",
        "core_available": read_document is not None,
        "write_available": write_document is not None,
        "description": "Document reading and writing utilities",
    }
    print_section("Documents Module Information")
    print(format_output(info, format_type="json"))
    print_section("", separator="")
    print_success("Information retrieved")
    return True


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Documents operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s read --file document.md
  %(prog)s info
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Read command
    read_parser = subparsers.add_parser("read", help="Read a document")
    read_parser.add_argument("--file", "-f", required=True, help="Document file path")
    
    # Info command
    subparsers.add_parser("info", help="Get module information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "read": handle_read,
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

