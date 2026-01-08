"""
Skills module orchestrator script.

Thin orchestrator script providing CLI access to skills module functionality.
Calls actual module functions from codomyrmex.skills.
"""

import argparse
import sys
from pathlib import Path

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
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
    )

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

logger = get_logger(__name__)


def handle_info(args):
    """Handle info command."""
    try:
        from codomyrmex import skills
        
        if getattr(args, "verbose", False):
            logger.info("Retrieving skills module information")

        info = {
            "module": "skills",
            "description": "Skills and capabilities management",
            "path": getattr(skills, "__path__", ["unknown"])[0],
        }

        print_section("Skills Module Information")
        print(format_output(info, format_type="json"))
        print_section("", separator="")
        return True
    
    except Exception as e:
        logger.exception("Unexpected error retrieving information")
        print_error("Unexpected error retrieving information", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Skills operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s info
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    subparsers.add_parser("info", help="Get skills module information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
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


if __name__ == "__main__":
    sys.exit(main())
