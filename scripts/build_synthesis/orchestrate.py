#!/usr/bin/env python3
"""
Build Synthesis Orchestrator

Thin orchestrator script providing CLI access to build_synthesis module functionality.
Calls actual module functions from codomyrmex.build_synthesis.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import json
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import BuildError, SynthesisError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        load_json_file,
        print_error,
        print_info,
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
        load_json_file,
        print_error,
        print_info,
        print_section,
        print_success,
        save_json_file,
        validate_file_path,
    )

# Import module functions
from codomyrmex.build_synthesis import (
    check_build_environment,
    orchestrate_build_pipeline,
    trigger_build,
    get_available_build_types,
    get_available_environments,
)

logger = get_logger(__name__)


def handle_check_environment(args):
    """Handle check build environment command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Checking build environment")

        result = check_build_environment()

        print_section("Build Environment Check")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        success = result.get("success", False) if isinstance(result, dict) else bool(result)
        if success:
            print_success("Build environment is ready")
        else:
            print_error("Build environment check failed")
        return success

    except BuildError as e:
        logger.error(f"Build error: {str(e)}")
        print_error("Build error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during environment check")
        print_error("Unexpected error during environment check", exception=e)
        return False


def handle_build(args):
    """Handle build command."""
    try:
        # Load build config if provided
        build_config = {}
        if args.config:
            config_path = validate_file_path(args.config, must_exist=True, must_be_file=True)
            build_config = load_json_file(config_path)

        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would build with config: {build_config}")
            return True

        if getattr(args, "verbose", False):
            logger.info(f"Starting build with config: {build_config}")

        result = orchestrate_build_pipeline(build_config)

        print_section("Build Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        success = result.get("success", False) if isinstance(result, dict) else bool(result)
        if success:
            print_success("Build completed successfully")
        else:
            print_error("Build failed")
        return success

    except (BuildError, SynthesisError) as e:
        logger.error(f"Build error: {str(e)}")
        print_error("Build error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during build")
        print_error("Unexpected error during build", exception=e)
        return False


def handle_trigger_build(args):
    """Handle trigger build command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would trigger build for target: {args.target}, environment: {args.environment}")
            return True

        if getattr(args, "verbose", False):
            logger.info(f"Triggering build for target: {args.target}, environment: {args.environment}")

        result = trigger_build(
            target_name=args.target,
            environment=args.environment,
        )

        print_section("Build Trigger Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        success = result.get("success", False) if isinstance(result, dict) else bool(result)
        if success:
            print_success("Build triggered successfully")
        else:
            print_error("Build trigger failed")
        return success

    except (BuildError, SynthesisError) as e:
        logger.error(f"Build error: {str(e)}")
        print_error("Build error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error triggering build")
        print_error("Unexpected error triggering build", exception=e)
        return False


def handle_list_build_types(args):
    """Handle list build types command."""
    try:
        build_types = get_available_build_types()

        print_section("Available Build Types")
        for build_type in build_types:
            print(f"  • {build_type}")
        print_section("", separator="")
        return True

    except Exception as e:
        logger.exception("Unexpected error listing build types")
        print_error("Unexpected error listing build types", exception=e)
        return False


def handle_list_environments(args):
    """Handle list environments command."""
    try:
        environments = get_available_environments()

        print_section("Available Build Environments")
        for env in environments:
            print(f"  • {env}")
        print_section("", separator="")
        return True

    except Exception as e:
        logger.exception("Unexpected error listing environments")
        print_error("Unexpected error listing environments", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Build Synthesis operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check-environment
  %(prog)s build --config build_config.json
  %(prog)s trigger-build --target python --environment production
  %(prog)s list-build-types
  %(prog)s list-environments
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

    # Check environment command
    subparsers.add_parser(
        "check-environment", help="Check build environment setup"
    )

    # Build command
    build_parser = subparsers.add_parser("build", help="Run build pipeline")
    build_parser.add_argument(
        "--config", "-c", help="Build configuration file (JSON)"
    )

    # Trigger build command
    trigger_parser = subparsers.add_parser(
        "trigger-build", help="Trigger a specific build target"
    )
    trigger_parser.add_argument(
        "--target", "-t", required=True, help="Build target name"
    )
    trigger_parser.add_argument(
        "--environment", "-e", help="Build environment"
    )

    # List build types command
    subparsers.add_parser(
        "list-build-types", help="List available build types"
    )

    # List environments command
    subparsers.add_parser(
        "list-environments", help="List available build environments"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "check-environment": handle_check_environment,
        "build": handle_build,
        "trigger-build": handle_trigger_build,
        "list-build-types": handle_list_build_types,
        "list-environments": handle_list_environments,
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

