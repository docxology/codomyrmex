#!/usr/bin/env python3
"""
Environment Setup Orchestrator

Thin orchestrator script providing CLI access to environment_setup module functionality.
Calls actual module functions from codomyrmex.environment_setup.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import EnvironmentError, DependencyError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
        print_warning,
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
        print_warning,
    )

# Import module functions
from codomyrmex.environment_setup import (
    check_and_setup_env_vars,
    ensure_dependencies_installed,
    is_uv_available,
    is_uv_environment,
)

logger = get_logger(__name__)


def handle_check_dependencies(args):
    """Handle check dependencies command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Checking dependencies")

        result = ensure_dependencies_installed()

        print_section("Dependency Check Results")
        if isinstance(result, dict):
            missing = result.get("missing", [])
            installed = result.get("installed", [])
            if missing:
                print("Missing dependencies:")
                for dep in missing:
                    print_error(f"{dep}", context="Missing")
            if installed:
                print("Installed dependencies:")
                for dep in installed:
                    print_success(f"{dep}", context="Installed")
            success = len(missing) == 0
        else:
            print(format_output(result, format_type="json"))
            success = bool(result)
        print_section("", separator="")

        if success:
            print_success("All dependencies are installed")
        else:
            print_error("Some dependencies are missing")
        return success

    except DependencyError as e:
        logger.error(f"Dependency error: {str(e)}")
        print_error("Dependency error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during dependency check")
        print_error("Unexpected error during dependency check", exception=e)
        return False


def handle_setup_env_vars(args):
    """Handle setup environment variables command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Checking and setting up environment variables")

        result = check_and_setup_env_vars()

        print_section("Environment Variables Setup")
        if isinstance(result, dict):
            missing = result.get("missing", [])
            set_vars = result.get("set", [])
            if missing:
                print("Missing environment variables:")
                for var in missing:
                    print_warning(f"{var}", context="Missing")
            if set_vars:
                print("Set environment variables:")
                for var in set_vars:
                    print_success(f"{var}", context="Set")
            success = len(missing) == 0
        else:
            print(format_output(result, format_type="json"))
            success = bool(result)
        print_section("", separator="")

        if success:
            print_success("All required environment variables are set")
        else:
            print_error("Some environment variables are missing")
        return success

    except EnvironmentError as e:
        logger.error(f"Environment error: {str(e)}")
        print_error("Environment error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during environment setup")
        print_error("Unexpected error during environment setup", exception=e)
        return False


def handle_check_uv(args):
    """Handle check UV availability command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Checking UV availability and environment")

        available = is_uv_available()
        is_env = is_uv_environment()

        print_section("UV Environment Check")
        if available:
            print_success("UV is available")
        else:
            print_error("UV is not available")
        if is_env:
            print_success("Running in UV environment")
        else:
            print_warning("Not running in UV environment")
        print_section("", separator="")

        return available

    except Exception as e:
        logger.exception("Unexpected error checking UV")
        print_error("Unexpected error checking UV", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Environment Setup operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check-dependencies
  %(prog)s setup-env-vars
  %(prog)s check-uv
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check dependencies command
    subparsers.add_parser(
        "check-dependencies", help="Check if all dependencies are installed"
    )

    # Setup environment variables command
    subparsers.add_parser(
        "setup-env-vars", help="Check and setup required environment variables"
    )

    # Check UV command
    subparsers.add_parser("check-uv", help="Check UV availability and environment")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "check-dependencies": handle_check_dependencies,
        "setup-env-vars": handle_setup_env_vars,
        "check-uv": handle_check_uv,
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

