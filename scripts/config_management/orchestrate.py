#!/usr/bin/env python3
"""
Config Management Orchestrator

Thin orchestrator script providing CLI access to config_management module functionality.
Calls actual module functions from codomyrmex.config_management.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import ConfigurationError, CodomyrmexError

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
from codomyrmex.config_management import (
    load_configuration,
    validate_configuration,
    manage_secrets,
    deploy_configuration,
)

logger = get_logger(__name__)


def handle_load_config(args):
    """Handle load configuration command."""
    try:
        config_path = validate_file_path(args.path, must_exist=True, must_be_file=True)
        
        if getattr(args, "verbose", False):
            logger.info(f"Loading configuration from {config_path}")

        result = load_configuration(config_path=str(config_path))

        print_section("Configuration Loaded")
        print(format_output(result, format_type="json"))
        print_section("", separator="")
        return True

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {args.path}")
        print_error("Configuration file not found", context=args.path, exception=e)
        return False
    except ValueError as e:
        logger.error(f"Invalid path: {args.path}")
        print_error("Invalid path", context=args.path, exception=e)
        return False
    except ConfigurationError as e:
        logger.error(f"Configuration error: {str(e)}")
        print_error("Configuration error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error loading configuration")
        print_error("Unexpected error loading configuration", exception=e)
        return False


def handle_validate_config(args):
    """Handle validate configuration command."""
    try:
        config_path = validate_file_path(args.path, must_exist=True, must_be_file=True)
        
        if getattr(args, "verbose", False):
            logger.info(f"Validating configuration from {config_path}")

        result = validate_configuration(config_path=str(config_path))

        print_section("Configuration Validation")
        if isinstance(result, dict):
            valid = result.get("valid", False)
            print(format_output(result, format_type="json"))
        else:
            print(format_output(result, format_type="json"))
            valid = bool(result)
        print_section("", separator="")

        if valid:
            print_success("Configuration is valid")
        else:
            print_error("Configuration is invalid")
        return valid

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {args.path}")
        print_error("Configuration file not found", context=args.path, exception=e)
        return False
    except ValueError as e:
        logger.error(f"Invalid path: {args.path}")
        print_error("Invalid path", context=args.path, exception=e)
        return False
    except ConfigurationError as e:
        logger.error(f"Configuration error: {str(e)}")
        print_error("Configuration error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error validating configuration")
        print_error("Unexpected error validating configuration", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Config Management operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s load-config --path config.json
  %(prog)s validate-config --path config.json
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

    # Load config command
    load_parser = subparsers.add_parser("load-config", help="Load configuration")
    load_parser.add_argument("--path", "-p", required=True, help="Configuration file path")

    # Validate config command
    validate_parser = subparsers.add_parser("validate-config", help="Validate configuration")
    validate_parser.add_argument("--path", "-p", required=True, help="Configuration file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "load-config": handle_load_config,
        "validate-config": handle_validate_config,
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

