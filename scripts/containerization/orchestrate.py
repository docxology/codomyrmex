#!/usr/bin/env python3
"""
Containerization Orchestrator

Thin orchestrator script providing CLI access to containerization module functionality.
Calls actual module functions from codomyrmex.containerization.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import ContainerError, CodomyrmexError

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

# Import module functions
from codomyrmex.containerization import build_containers, scan_container_security

logger = get_logger(__name__)


def handle_build(args):
    """Handle build containers command."""
    try:
        source_path = validate_file_path(args.source, must_exist=True, must_be_dir=True)
        
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would build containers from {source_path}")
            return True

        if getattr(args, "verbose", False):
            logger.info(f"Building containers from {source_path}")

        result = build_containers(source_path=str(source_path))

        print_section("Container Build")
        if isinstance(result, dict):
            success = result.get("success", False)
            print(format_output(result, format_type="json"))
        else:
            success = bool(result)
            print(format_output(result, format_type="json"))
        print_section("", separator="")

        if success:
            print_success("Containers built successfully")
        else:
            print_error("Container build failed")
        return success

    except FileNotFoundError as e:
        logger.error(f"Source directory not found: {args.source}")
        print_error("Source directory not found", context=args.source, exception=e)
        return False
    except ValueError as e:
        logger.error(f"Invalid source path: {args.source}")
        print_error("Invalid source path", context=args.source, exception=e)
        return False
    except ContainerError as e:
        logger.error(f"Container error: {str(e)}")
        print_error("Container error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error building containers")
        print_error("Unexpected error building containers", exception=e)
        return False


def handle_scan(args):
    """Handle scan container security command."""
    try:
        if getattr(args, "verbose", False):
            logger.info(f"Scanning container security: {args.container}")

        result = scan_container_security(container_name=args.container)

        print_section("Container Security Scan")
        print(format_output(result, format_type="json"))
        print_section("", separator="")
        return True

    except ContainerError as e:
        logger.error(f"Container error: {str(e)}")
        print_error("Container error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error scanning container")
        print_error("Unexpected error scanning container", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Containerization operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s build --source .
  %(prog)s scan --container my-container
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Dry run mode (no changes)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build containers")
    build_parser.add_argument("--source", "-s", default=".", help="Source path")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan container security")
    scan_parser.add_argument("--container", "-c", required=True, help="Container name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "build": handle_build,
        "scan": handle_scan,
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

