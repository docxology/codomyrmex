#!/usr/bin/env python3
"""
Performance Orchestrator

Thin orchestrator script providing CLI access to performance module functionality.
Calls actual module functions from codomyrmex.performance.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import PerformanceError, CodomyrmexError

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
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
        save_json_file,
        validate_file_path,
    )

# Import module functions
try:
    from codomyrmex.performance import PerformanceMonitor
    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITOR_AVAILABLE = False

from codomyrmex.performance import CacheManager, LazyLoader

logger = get_logger(__name__)


def handle_monitor_stats(args):
    """Handle monitor stats command."""
    try:
        if not PERFORMANCE_MONITOR_AVAILABLE:
            print_error("PerformanceMonitor is not available", context="psutil may be missing")
            return False

        if getattr(args, "verbose", False):
            logger.info("Getting performance monitor statistics")

        monitor = PerformanceMonitor()
        stats = monitor.get_stats()

        print_section("Performance Monitor Stats")
        print(format_output(stats, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(stats, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except PerformanceError as e:
        logger.error(f"Performance error: {str(e)}")
        print_error("Performance error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error getting monitor stats")
        print_error("Unexpected error getting monitor stats", exception=e)
        return False


def handle_cache_info(args):
    """Handle cache info command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Getting cache manager information")

        cache = CacheManager()
        info = {
            "cache_available": True,
            "description": "Cache manager is available"
        }

        print_section("Cache Manager Info")
        print(format_output(info, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(info, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except PerformanceError as e:
        logger.error(f"Performance error: {str(e)}")
        print_error("Performance error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error getting cache info")
        print_error("Unexpected error getting cache info", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Performance operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s monitor-stats
  %(prog)s cache-info
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Monitor stats command
    monitor_parser = subparsers.add_parser("monitor-stats", help="Get performance monitor statistics")
    monitor_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    # Cache info command
    cache_parser = subparsers.add_parser("cache-info", help="Get cache manager information")
    cache_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "monitor-stats": handle_monitor_stats,
        "cache-info": handle_cache_info,
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

