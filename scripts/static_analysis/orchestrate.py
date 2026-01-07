#!/usr/bin/env python3
"""
Static Analysis Orchestrator

Thin orchestrator script providing CLI access to static_analysis module functionality.
Calls actual module functions from codomyrmex.static_analysis.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import json
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import StaticAnalysisError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
        save_json_file,
        validate_file_path,
        ProgressReporter,
        validate_dry_run,
        enhanced_error_context,
        create_dry_run_plan,
        add_common_arguments,
        print_with_color,
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
        save_json_file,
        validate_file_path,
        ProgressReporter,
        validate_dry_run,
        enhanced_error_context,
        create_dry_run_plan,
        add_common_arguments,
        print_with_color,
    )

# Import module functions
from codomyrmex.static_analysis import (
    analyze_file,
    analyze_project,
    get_available_tools,
)

logger = get_logger(__name__)


def handle_analyze_file(args):
    """Handle file analysis command."""
    try:
        file_path = validate_file_path(args.file, must_exist=True, must_be_file=True)

        if getattr(args, "verbose", False):
            logger.info(f"Analyzing file: {file_path}")

        result = analyze_file(str(file_path))

        print_section("Analysis Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(result, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except FileNotFoundError as e:
        logger.error(f"File not found: {args.file}")
        print_error("File not found", context=str(args.file))
        return False
    except StaticAnalysisError as e:
        logger.error(f"Static analysis error: {str(e)}")
        print_error("Static analysis error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during file analysis")
        print_error("Unexpected error during file analysis", exception=e)
        return False


def handle_analyze_project(args):
    """Handle project analysis command."""
    try:
        project_path = validate_file_path(
            args.path if args.path else ".",
            must_exist=True,
            must_be_dir=True,
        )

        if getattr(args, "verbose", False):
            logger.info(f"Analyzing project: {project_path}")

        # Initialize progress reporter for multi-step analysis
        progress = ProgressReporter(total=4, prefix="Analyzing Project")

        # Step 1: Discover project files
        progress.update(message="Discovering project files...")
        # File discovery happens during analysis

        # Step 2: Initialize analysis tools
        progress.update(message="Initializing analysis tools...")

        # Step 3: Run comprehensive analysis
        progress.update(message="Running comprehensive analysis...")
        result = analyze_project(str(project_path))

        # Step 4: Generate summary
        progress.update(message="Generating analysis summary...")
        files_analyzed = result.get("files_analyzed", 0) if isinstance(result, dict) else 0
        issues_found = 0
        if isinstance(result, dict) and "results" in result:
            issues_found = sum(len(issues) for issues in result["results"].values())

        progress.complete(message=f"Analysis complete: {files_analyzed} files analyzed, {issues_found} issues found")

        # Display results with enhanced formatting
        print_section("Project Analysis Results")
        print_with_color(f"Files analyzed: {files_analyzed}", "blue")
        print_with_color(f"Total issues found: {issues_found}", "yellow" if issues_found > 0 else "green")

        output_format = getattr(args, 'format', 'text')
        if output_format == 'json' or isinstance(result, dict):
            print(format_output(result, format_type="json"))
            if isinstance(result, dict):
                score = result.get("score", "N/A")
                if score != "N/A":
                    print_with_color(f"\nQuality Score: {score}/10", "green" if score >= 7 else "yellow" if score >= 5 else "red")
        else:
            print(format_output(result, format_type="text"))

        print_section("", separator="")

        if args.output:
            output_path = save_json_file(result, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except StaticAnalysisError as e:
        logger.error(f"Static analysis error: {str(e)}")
        print_error("Static analysis error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during project analysis")
        print_error("Unexpected error during project analysis", exception=e)
        return False


def handle_list_tools(args):
    """Handle list tools command."""
    try:
        tools = get_available_tools()

        print_section("Available Analysis Tools")
        for tool in tools:
            print(f"  • {tool}")
        print_section("", separator="")
        return True

    except Exception as e:
        logger.exception("Unexpected error listing tools")
        print_error("Unexpected error listing tools", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Static Analysis operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze-file file.py --output results.json
  %(prog)s analyze-project . --output analysis_report.json --dry-run
  %(prog)s list-tools --format json
  %(prog)s analyze-file file.py --verbose
        """,
    )

    # Add common arguments
    add_common_arguments(parser)

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze file command
    file_parser = subparsers.add_parser("analyze-file", help="Analyze a single file")
    file_parser.add_argument("file", help="File to analyze")
    file_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    # Analyze project command
    project_parser = subparsers.add_parser(
        "analyze-project", help="Analyze an entire project"
    )
    project_parser.add_argument(
        "path", nargs="?", default=".", help="Project path (default: current directory)"
    )
    project_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    # List tools command
    subparsers.add_parser("list-tools", help="List available analysis tools")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Validate dry-run mode
    if not validate_dry_run(args):
        return 0

    # Create execution plan for dry-run
    if getattr(args, 'dry_run', False):
        operations = []
        if args.command == 'analyze-file':
            operations.append({
                "description": f"Analyze file: {args.file}",
                "details": f"Output: {args.output or 'console'}",
                "target": args.file
            })
        elif args.command == 'analyze-project':
            operations.append({
                "description": f"Analyze project: {args.path}",
                "details": f"Output: {args.output or 'console'}",
                "target": args.path
            })

        print(create_dry_run_plan(args, operations))
        return 0

    # Route to appropriate handler with enhanced error context
    handlers = {
        "analyze-file": handle_analyze_file,
        "analyze-project": handle_analyze_project,
        "list-tools": handle_list_tools,
    }

    handler = handlers.get(args.command)
    if handler:
        command_context = {
            "command": args.command,
            "format": getattr(args, 'format', 'text'),
            "dry_run": getattr(args, 'dry_run', False)
        }

        try:
            with enhanced_error_context(f"static_analysis_{args.command}", command_context):
                success = handler(args)
                return 0 if success else 1
        except Exception as e:
            logger.error(f"Error in command '{args.command}': {e}", exc_info=True)
            print_error(f"Command failed: {e}")
            print_with_color("Troubleshooting tips:", "yellow")
            print_with_color("1. Check that the file/directory exists and is accessible", "yellow")
            print_with_color("2. Ensure analysis tools are installed (e.g., flake8, pylint)", "yellow")
            print_with_color("3. Try running with --verbose for detailed output", "yellow")
            return 1
    else:
        print_error("Unknown command", context=args.command)
        return 1


if __name__ == "__main__":
    sys.exit(main())

