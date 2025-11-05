#!/usr/bin/env python3
"""
Code Review Orchestrator

Thin orchestrator script providing CLI access to code_review module functionality.
Calls actual module functions from codomyrmex.code_review.

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
        ensure_output_directory,
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
        ensure_output_directory,
        format_output,
        print_error,
        print_section,
        print_success,
        validate_file_path,
    )

# Import module functions and exceptions
from codomyrmex.code_review import (
    CodeReviewError,
    analyze_file,
    analyze_project,
    generate_report,
)

logger = get_logger(__name__)


def handle_analyze_file(args):
    """Handle analyze file command."""
    try:
        # Validate file exists
        file_path = validate_file_path(args.file, must_exist=True, must_be_file=True)

        if getattr(args, "verbose", False):
            logger.info(f"Analyzing file: {file_path}")

        result = analyze_file(str(file_path))

        print_section("Code Review Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        print_success("File analysis completed")
        return True

    except CodeReviewError as e:
        logger.error(f"Code review error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Code review error", context=str(e), exception=e)
        return False
    except FileNotFoundError as e:
        logger.error(f"File not found: {args.file}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("File not found", context=args.file, exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during code review")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error during code review", exception=e)
        return False


def handle_analyze_project(args):
    """Handle analyze project command."""
    try:
        # Validate project path exists
        project_path = validate_file_path(args.path, must_exist=True, must_be_dir=True)

        if getattr(args, "verbose", False):
            logger.info(f"Analyzing project: {project_path}")

        result = analyze_project(path=str(project_path))

        print_section("Project Code Review Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        print_success("Project analysis completed")
        return True

    except CodeReviewError as e:
        logger.error(f"Code review error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Code review error", context=str(e), exception=e)
        return False
    except FileNotFoundError as e:
        logger.error(f"Project path not found: {args.path}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Project path not found", context=args.path, exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during project review")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error during project review", exception=e)
        return False


def handle_generate_report(args):
    """Handle generate report command."""
    try:
        # Validate project path exists
        project_path = validate_file_path(args.path, must_exist=True, must_be_dir=True)
        # Ensure output directory exists
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Generating code review report from {project_path} to {output_path}")

        result = generate_report(path=str(project_path), output=str(output_path))

        print_section("Code Review Report")
        if isinstance(result, dict):
            print(format_output(result, format_type="json"))
            success = result.get("success", False)
        else:
            print(format_output(result))
            success = bool(result)
        print_section("", separator="")

        if success:
            print_success("Report generated", context=str(output_path))
        else:
            print_error("Report generation failed")
        return success

    except CodeReviewError as e:
        logger.error(f"Code review error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Code review error", context=str(e), exception=e)
        return False
    except FileNotFoundError as e:
        logger.error(f"Project path not found: {args.path}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Project path not found", context=args.path, exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error generating report")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error generating report", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Code Review operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze-file file.py
  %(prog)s analyze-project --path src/
  %(prog)s generate-report --path src/ --output report.json
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze file command
    file_parser = subparsers.add_parser("analyze-file", help="Analyze a single file")
    file_parser.add_argument("file", help="File to analyze")

    # Analyze project command
    project_parser = subparsers.add_parser("analyze-project", help="Analyze a project")
    project_parser.add_argument("--path", "-p", default=".", help="Project path")

    # Generate report command
    report_parser = subparsers.add_parser("generate-report", help="Generate review report")
    report_parser.add_argument("--path", "-p", default=".", help="Project path")
    report_parser.add_argument("--output", "-o", required=True, help="Output file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "analyze-file": handle_analyze_file,
        "analyze-project": handle_analyze_project,
        "generate-report": handle_generate_report,
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

