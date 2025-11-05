#!/usr/bin/env python3
"""
System Discovery Orchestrator

Thin orchestrator script providing CLI access to system_discovery module functionality.
Calls actual module functions from codomyrmex.system_discovery.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import SystemDiscoveryError, CapabilityScanError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
        save_json_file,
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
        save_json_file,
        validate_file_path,
    )

# Import module functions
from codomyrmex.system_discovery import (
    CapabilityScanner,
    StatusReporter,
    SystemDiscovery,
)

logger = get_logger(__name__)


def handle_status(args):
    """Handle status report command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Generating system status report")

        reporter = StatusReporter()
        report = reporter.generate_comprehensive_report()

        print_section("System Status Report")
        print(format_output(report, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(report, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except SystemDiscoveryError as e:
        logger.error(f"System discovery error: {str(e)}")
        print_error("System discovery error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error generating status report")
        print_error("Unexpected error generating status report", exception=e)
        return False


def handle_scan(args):
    """Handle capability scan command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Scanning system capabilities")

        scanner = CapabilityScanner()
        capabilities = scanner.scan_capabilities()

        print_section("Capability Scan Results")
        print(format_output(capabilities, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(capabilities, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except CapabilityScanError as e:
        logger.error(f"Capability scan error: {str(e)}")
        print_error("Capability scan error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during capability scan")
        print_error("Unexpected error during capability scan", exception=e)
        return False


def handle_discover(args):
    """Handle system discovery command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Discovering system components")

        discovery = SystemDiscovery()
        result = discovery.discover_system()

        print_section("System Discovery Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(result, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except SystemDiscoveryError as e:
        logger.error(f"System discovery error: {str(e)}")
        print_error("System discovery error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during system discovery")
        print_error("Unexpected error during system discovery", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="System Discovery operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status
  %(prog)s scan
  %(prog)s discover
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Generate system status report")
    status_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan system capabilities")
    scan_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    # Discover command
    discover_parser = subparsers.add_parser("discover", help="Discover system components")
    discover_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "status": handle_status,
        "scan": handle_scan,
        "discover": handle_discover,
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

