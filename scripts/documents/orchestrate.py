#!/usr/bin/env python3
"""
Documents Module Orchestrator

Thin orchestrator script providing CLI access to documents module functionality.
Calls actual module functions from codomyrmex.documents.

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
    sys.path.insert(0, str(Path(__file__).parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
        validate_file_path,
    )

# Import module functions
from codomyrmex.documents import process_document

logger = get_logger(__name__)


def handle_process(args):
    """Handle document processing command."""
    try:
        file_path = validate_file_path(args.file, must_exist=True, must_be_file=True)

        if getattr(args, "verbose", False):
            logger.info(f"Processing document: {file_path}")

        result = process_document(str(file_path))

        print_section("Document Processing Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        print_success("Document processed successfully")
        return True

    except Exception as e:
        logger.exception("Unexpected error processing document")
        print_error("Unexpected error processing document", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Documents operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s process --file document.pdf
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process a document")
    process_parser.add_argument("--file", "-f", required=True, help="Document file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "process": handle_process,
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

