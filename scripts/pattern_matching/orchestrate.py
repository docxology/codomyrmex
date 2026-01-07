#!/usr/bin/env python3
"""
Pattern Matching Orchestrator

Thin orchestrator script providing CLI access to pattern_matching module functionality.
Calls actual module functions from codomyrmex.pattern_matching.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import json
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import PatternMatchingError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
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
        print_info,
        print_section,
        print_success,
        validate_file_path,
    )

# Import module functions - handle missing dependencies
try:
    from codomyrmex.pattern_matching import (
        analyze_repository_path,
        run_full_analysis,
    )
    PATTERN_MATCHING_AVAILABLE = True
except ImportError as e:
    analyze_repository_path = None
    run_full_analysis = None
    PATTERN_MATCHING_AVAILABLE = False
    _import_error = str(e)

logger = get_logger(__name__)


def handle_info(args):
    """Handle info command."""
    info = {
        "module": "pattern_matching",
        "available": PATTERN_MATCHING_AVAILABLE,
        "error": _import_error if not PATTERN_MATCHING_AVAILABLE else None,
        "description": "Code pattern analysis and repository scanning",
    }
    print_section("Pattern Matching Module Information")
    print(format_output(info, format_type="json"))
    print_section("", separator="")
    if not PATTERN_MATCHING_AVAILABLE:
        print_error(f"Module not available: {_import_error}")
        return False
    print_success("Information retrieved")
    return True


def handle_analyze(args):
    """Handle analyze repository command."""
    if not PATTERN_MATCHING_AVAILABLE:
        print_error(f"Pattern matching not available: {_import_error}")
        return False
    try:
        repo_path = validate_file_path(
            args.path if args.path else ".",
            must_exist=True,
            must_be_dir=True
        )

        if getattr(args, "verbose", False):
            logger.info(f"Analyzing repository path: {repo_path}")

        result = analyze_repository_path(str(repo_path))

        print_section("Pattern Matching Analysis")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = validate_file_path(
                args.output,
                must_exist=False
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(result if isinstance(result, dict) else {"result": result}, f, indent=2)
            if getattr(args, "verbose", False):
                logger.info(f"Results saved to: {output_path}")
            print_success(f"Results saved to: {output_path}")
        else:
            print_success("Analysis completed")
        return True

    except PatternMatchingError as e:
        logger.error(f"Pattern matching error: {str(e)}")
        print_error("Pattern matching error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        print_error("File not found", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error during pattern matching")
        print_error("Unexpected error during pattern matching", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def handle_full_analysis(args):
    """Handle full analysis command."""
    if not PATTERN_MATCHING_AVAILABLE:
        print_error(f"Pattern matching not available: {_import_error}")
        return False
    try:
        repo_path = validate_file_path(
            args.path if args.path else ".",
            must_exist=True,
            must_be_dir=True
        )

        if getattr(args, "verbose", False):
            logger.info(f"Running full analysis on repository path: {repo_path}")

        result = run_full_analysis(str(repo_path))

        print_section("Full Pattern Matching Analysis")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = validate_file_path(
                args.output,
                must_exist=False
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(result if isinstance(result, dict) else {"result": result}, f, indent=2)
            if getattr(args, "verbose", False):
                logger.info(f"Results saved to: {output_path}")
            print_success(f"Results saved to: {output_path}")
        else:
            print_success("Full analysis completed")
        return True

    except PatternMatchingError as e:
        logger.error(f"Pattern matching error: {str(e)}")
        print_error("Pattern matching error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        print_error("File not found", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error during full analysis")
        print_error("Unexpected error during full analysis", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Pattern Matching operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze --path src/
  %(prog)s full-analysis --path . --output results.json
  %(prog)s analyze --path src/ --verbose
  %(prog)s full-analysis --path . --output results.json --verbose
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    subparsers.add_parser("info", help="Get module information")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze repository patterns")
    analyze_parser.add_argument("path", nargs="?", default=".", help="Repository path")
    analyze_parser.add_argument("--output", "-o", help="Output file path")

    # Full analysis command
    full_parser = subparsers.add_parser("full-analysis", help="Run full pattern analysis")
    full_parser.add_argument("path", nargs="?", default=".", help="Repository path")
    full_parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "info": handle_info,
        "analyze": handle_analyze,
        "full-analysis": handle_full_analysis,
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

