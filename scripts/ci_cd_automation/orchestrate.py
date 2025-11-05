#!/usr/bin/env python3
"""
CI/CD Automation Orchestrator

Thin orchestrator script providing CLI access to ci_cd_automation module functionality.
Calls actual module functions from codomyrmex.ci_cd_automation.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import json
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import CICDError, DeploymentError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
    )

# Import module functions
from codomyrmex.ci_cd_automation import (
    create_pipeline,
    generate_pipeline_reports,
    handle_rollback,
    manage_deployments,
    monitor_pipeline_health,
    run_pipeline,
)

logger = get_logger(__name__)


def handle_create_pipeline(args):
    """Handle create pipeline command."""
    try:
        if getattr(args, "verbose", False):
            logger.info(f"Creating pipeline: {args.name}")
            if args.config:
                logger.info(f"Configuration: {args.config}")

        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would create pipeline: {args.name}")
            if args.config:
                print_info(f"Configuration: {args.config}")
            return True

        # Handle config: could be a file path or JSON string
        config = {}
        if args.config:
            config_path = Path(args.config)
            if config_path.exists() and config_path.is_file():
                # Load from file
                try:
                    from _orchestrator_utils import load_json_file
                except ImportError:
                    import json
                    with open(config_path, "r") as f:
                        config = json.load(f)
                else:
                    config = load_json_file(config_path)
                if getattr(args, "verbose", False):
                    logger.info(f"Loaded configuration from file: {config_path}")
            else:
                # Try to parse as JSON string
                try:
                    config = json.loads(args.config)
                    if getattr(args, "verbose", False):
                        logger.info("Parsed configuration from JSON string")
                except json.JSONDecodeError:
                    print_error("Invalid JSON configuration", context="Config must be a valid JSON string or file path")
                    return False

        result = create_pipeline(
            name=args.name,
            config=config,
        )

        print_section("Pipeline Creation")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        success = result.get("success", False) if isinstance(result, dict) else bool(result)
        if success:
            print_success(f"Pipeline '{args.name}' created successfully")
        else:
            print_error("Pipeline creation failed", context=args.name)
        return success

    except CICDError as e:
        logger.error(f"CI/CD error: {str(e)}")
        print_error("CI/CD error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except DeploymentError as e:
        logger.error(f"Deployment error: {str(e)}")
        print_error("Deployment error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error creating pipeline")
        print_error("Unexpected error creating pipeline", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def handle_run_pipeline(args):
    """Handle run pipeline command."""
    try:
        if getattr(args, "verbose", False):
            logger.info(f"Running pipeline: {args.name}")

        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would run pipeline: {args.name}")
            return True

        result = run_pipeline(pipeline_name=args.name)

        print_section("Pipeline Execution")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        success = result.get("success", False) if isinstance(result, dict) else bool(result)
        if success:
            print_success(f"Pipeline '{args.name}' executed successfully")
        else:
            print_error("Pipeline execution failed", context=args.name)
        return success

    except CICDError as e:
        logger.error(f"CI/CD error: {str(e)}")
        print_error("CI/CD error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except DeploymentError as e:
        logger.error(f"Deployment error: {str(e)}")
        print_error("Deployment error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error running pipeline")
        print_error("Unexpected error running pipeline", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def handle_monitor_health(args):
    """Handle monitor pipeline health command."""
    try:
        if getattr(args, "verbose", False):
            logger.info(f"Monitoring pipeline health: {args.name}")

        result = monitor_pipeline_health(pipeline_name=args.name)

        print_section("Pipeline Health")
        print(format_output(result, format_type="json"))
        print_section("", separator="")
        return True

    except CICDError as e:
        logger.error(f"CI/CD error: {str(e)}")
        print_error("CI/CD error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except DeploymentError as e:
        logger.error(f"Deployment error: {str(e)}")
        print_error("Deployment error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error monitoring pipeline health")
        print_error("Unexpected error monitoring pipeline health", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def handle_generate_reports(args):
    """Handle generate pipeline reports command."""
    try:
        if getattr(args, "verbose", False):
            logger.info(f"Generating pipeline reports: {args.name}")

        result = generate_pipeline_reports(pipeline_name=args.name)

        print_section("Pipeline Reports")
        print(format_output(result, format_type="json"))
        print_section("", separator="")
        return True

    except CICDError as e:
        logger.error(f"CI/CD error: {str(e)}")
        print_error("CI/CD error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except DeploymentError as e:
        logger.error(f"Deployment error: {str(e)}")
        print_error("Deployment error", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error generating reports")
        print_error("Unexpected error generating reports", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="CI/CD Automation operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create-pipeline --name my-pipeline
  %(prog)s run-pipeline --name my-pipeline
  %(prog)s run-pipeline --name my-pipeline --dry-run
  %(prog)s monitor-health --name my-pipeline
  %(prog)s generate-reports --name my-pipeline
  %(prog)s run-pipeline --name my-pipeline --verbose --dry-run
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

    # Create pipeline command
    create_parser = subparsers.add_parser("create-pipeline", help="Create CI/CD pipeline")
    create_parser.add_argument("--name", "-n", required=True, help="Pipeline name")
    create_parser.add_argument("--config", "-c", help="Pipeline configuration (JSON)")

    # Run pipeline command
    run_parser = subparsers.add_parser("run-pipeline", help="Run CI/CD pipeline")
    run_parser.add_argument("--name", "-n", required=True, help="Pipeline name")

    # Monitor health command
    monitor_parser = subparsers.add_parser("monitor-health", help="Monitor pipeline health")
    monitor_parser.add_argument("--name", "-n", required=True, help="Pipeline name")

    # Generate reports command
    reports_parser = subparsers.add_parser("generate-reports", help="Generate pipeline reports")
    reports_parser.add_argument("--name", "-n", required=True, help="Pipeline name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "create-pipeline": handle_create_pipeline,
        "run-pipeline": handle_run_pipeline,
        "monitor-health": handle_monitor_health,
        "generate-reports": handle_generate_reports,
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

