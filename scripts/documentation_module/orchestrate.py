#!/usr/bin/env python3
"""
Documentation Module Orchestrator

Thin orchestrator script providing CLI access to documentation module functionality.
Calls actual module functions from codomyrmex.documentation.

Note: This is for the codomyrmex.documentation module, not the scripts/documentation/ utilities.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import DocumentationError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        ensure_output_directory,
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
    sys.path.insert(0, str(Path(__file__).parent))
    from _orchestrator_utils import (
        ensure_output_directory,
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        validate_file_path,
    )

# Import module functions
from codomyrmex.documentation import (
    aggregate_docs,
    assess_site,
    build_static_site,
    check_doc_environment,
    start_dev_server,
    validate_doc_versions,
)

logger = get_logger(__name__)


def handle_check_environment(args):
    """Handle check doc environment command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Checking documentation environment")

        result = check_doc_environment()

        print_section("Documentation Environment Check")
        if isinstance(result, dict):
            print(format_output(result, format_type="json"))
            ready = result.get("ready", False)
        else:
            print(format_output(result))
            ready = bool(result)
        print_section("", separator="")

        if ready:
            print_success("Documentation environment is ready")
        else:
            print_error("Documentation environment is not ready")
        return ready

    except DocumentationError as e:
        logger.error(f"Documentation error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Documentation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error checking doc environment")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error checking doc environment", exception=e)
        return False


def handle_build(args):
    """Handle build static site command."""
    try:
        # Ensure output directory exists
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Building documentation site: {output_path}")

        result = build_static_site(output_dir=str(output_path))

        print_section("Documentation Build")
        if isinstance(result, dict):
            print(format_output(result, format_type="json"))
            success = result.get("success", False)
        else:
            print(format_output(result))
            success = bool(result)
        print_section("", separator="")

        if success:
            print_success("Documentation built", context=str(output_path))
        else:
            print_error("Documentation build failed")
        return success

    except DocumentationError as e:
        logger.error(f"Documentation error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Documentation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error building documentation")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error building documentation", exception=e)
        return False


def handle_dev_server(args):
    """Handle start dev server command."""
    try:
        if getattr(args, "verbose", False):
            logger.info(f"Starting documentation dev server on port {args.port}")

        print_info("Starting documentation dev server...")
        print_info("Press Ctrl+C to stop")
        result = start_dev_server(port=args.port)
        return True

    except DocumentationError as e:
        logger.error(f"Documentation error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Documentation error", context=str(e), exception=e)
        return False
    except KeyboardInterrupt:
        print_success("Dev server stopped")
        return True
    except Exception as e:
        logger.exception("Unexpected error starting dev server")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error starting dev server", exception=e)
        return False


def handle_aggregate(args):
    """Handle aggregate docs command."""
    try:
        # Validate source directory exists
        source_path = validate_file_path(args.source, must_exist=True, must_be_dir=True)
        # Ensure output directory exists
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Aggregating documentation from {source_path} to {output_path}")

        result = aggregate_docs(source_dir=str(source_path), output_dir=str(output_path))

        print_section("Documentation Aggregation")
        if isinstance(result, dict):
            print(format_output(result, format_type="json"))
            success = result.get("success", False)
        else:
            print(format_output(result))
            success = bool(result)
        print_section("", separator="")

        if success:
            print_success("Documentation aggregated", context=str(output_path))
        else:
            print_error("Documentation aggregation failed")
        return success

    except DocumentationError as e:
        logger.error(f"Documentation error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Documentation error", context=str(e), exception=e)
        return False
    except FileNotFoundError as e:
        logger.error(f"Source directory not found: {args.source}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Source directory not found", context=args.source, exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error aggregating documentation")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error aggregating documentation", exception=e)
        return False


def handle_assess(args):
    """Handle assess site command."""
    try:
        # Validate site directory exists
        site_path = validate_file_path(args.path, must_exist=True, must_be_dir=True)

        if getattr(args, "verbose", False):
            logger.info(f"Assessing documentation site: {site_path}")

        result = assess_site(site_dir=str(site_path))

        print_section("Documentation Site Assessment")
        if isinstance(result, dict):
            print(format_output(result, format_type="json"))
        else:
            print(format_output(result))
        print_section("", separator="")

        print_success("Assessment completed")
        return True

    except DocumentationError as e:
        logger.error(f"Documentation error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Documentation error", context=str(e), exception=e)
        return False
    except FileNotFoundError as e:
        logger.error(f"Site directory not found: {args.path}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Site directory not found", context=args.path, exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error assessing site")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error assessing site", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Documentation Module operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check-environment
  %(prog)s build --output docs/build/
  %(prog)s dev-server --port 3000
  %(prog)s aggregate --source docs/ --output docs/aggregated/
  %(prog)s assess --path docs/build/
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check environment command
    subparsers.add_parser("check-environment", help="Check documentation environment")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build static documentation site")
    build_parser.add_argument("--output", "-o", default="docs/build/", help="Output directory")

    # Dev server command
    dev_parser = subparsers.add_parser("dev-server", help="Start development server")
    dev_parser.add_argument("--port", "-p", type=int, default=3000, help="Server port")

    # Aggregate command
    agg_parser = subparsers.add_parser("aggregate", help="Aggregate documentation")
    agg_parser.add_argument("--source", "-s", required=True, help="Source directory")
    agg_parser.add_argument("--output", "-o", required=True, help="Output directory")

    # Assess command
    assess_parser = subparsers.add_parser("assess", help="Assess documentation site")
    assess_parser.add_argument("--path", "-p", required=True, help="Site directory")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "check-environment": handle_check_environment,
        "build": handle_build,
        "dev-server": handle_dev_server,
        "aggregate": handle_aggregate,
        "assess": handle_assess,
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

