#!/usr/bin/env python3
"""
Tools Module Orchestrator

Thin orchestrator script providing CLI access to tools module functionality.
Calls actual module functions from codomyrmex.tools.

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
from codomyrmex.tools import analyze_project_structure, analyze_project_dependencies

logger = get_logger(__name__)


def handle_analyze_structure(args):
    """Handle analyze project structure command."""
    try:
        project_path = validate_file_path(args.path, must_exist=True, must_be_dir=True)

        if getattr(args, "verbose", False):
            logger.info(f"Analyzing project structure: {project_path}")

        result = analyze_project_structure(str(project_path))

        print_section("Project Structure Analysis")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        print_success("Analysis completed")
        return True

    except Exception as e:
        logger.exception("Unexpected error analyzing project structure")
        print_error("Unexpected error analyzing project structure", exception=e)
        return False


def handle_analyze_dependencies(args):
    """Handle analyze dependencies command."""
    try:
        project_path = validate_file_path(args.path, must_exist=True, must_be_dir=True)

        if getattr(args, "verbose", False):
            logger.info(f"Analyzing project dependencies: {project_path}")

        result = analyze_project_dependencies(str(project_path))

        print_section("Dependency Analysis")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        print_success("Analysis completed")
        return True

    except Exception as e:
        logger.exception("Unexpected error analyzing dependencies")
        print_error("Unexpected error analyzing dependencies", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Tools operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze-structure --path src/
  %(prog)s analyze-dependencies --path src/
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze structure command
    structure_parser = subparsers.add_parser("analyze-structure", help="Analyze project structure")
    structure_parser.add_argument("--path", "-p", default=".", help="Project path")

    # Analyze dependencies command
    deps_parser = subparsers.add_parser("analyze-dependencies", help="Analyze project dependencies")
    deps_parser.add_argument("--path", "-p", default=".", help="Project path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "analyze-structure": handle_analyze_structure,
        "analyze-dependencies": handle_analyze_dependencies,
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


