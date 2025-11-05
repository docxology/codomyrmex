#!/usr/bin/env python3
"""
Project Orchestration Orchestrator

Thin orchestrator script providing CLI access to project_orchestration module functionality.
Calls actual module functions from codomyrmex.project_orchestration.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import json
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import (
    OrchestrationError,
    WorkflowError,
    ProjectManagementError,
    CodomyrmexError,
)

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
    sys.path.insert(0, str(Path(__file__).parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
    )

# Import module functions
from codomyrmex.project_orchestration import (
    get_workflow_manager,
    get_project_manager,
    get_orchestration_engine,
    WorkflowStep,
)

logger = get_logger(__name__)


def handle_list_workflows(args):
    """Handle list workflows command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Listing available workflows")

        manager = get_workflow_manager()
        workflows = manager.list_workflows()

        print_section("Available Workflows")
        if workflows:
            for name, info in workflows.items():
                print(f"  • {name}")
                if isinstance(info, dict):
                    print(f"    Steps: {info.get('steps', 'N/A')}")
                    print(f"    Modules: {', '.join(info.get('modules', []))}")
        else:
            print("  No workflows available")
        print_section("", separator="")
        return True

    except OrchestrationError as e:
        logger.error(f"Orchestration error: {str(e)}")
        print_error("Orchestration error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error listing workflows")
        print_error("Unexpected error listing workflows", exception=e)
        return False


def handle_run_workflow(args):
    """Handle run workflow command."""
    try:
        if getattr(args, "verbose", False):
            logger.info(f"Running workflow: {args.name}")

        engine = get_orchestration_engine()
        result = engine.execute_workflow(args.name, **{})

        print_section("Workflow Execution Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        success = result.get("success", False) if isinstance(result, dict) else bool(result)
        if success:
            print_success(f"Workflow '{args.name}' completed successfully")
        else:
            print_error(f"Workflow '{args.name}' failed")
        return success

    except (WorkflowError, OrchestrationError) as e:
        logger.error(f"Workflow error: {str(e)}")
        print_error("Workflow error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error running workflow")
        print_error("Unexpected error running workflow", exception=e)
        return False


def handle_list_projects(args):
    """Handle list projects command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Listing available projects")

        manager = get_project_manager()
        projects = manager.list_projects()

        print_section("Available Projects")
        if projects:
            for project_name in projects:
                project = manager.get_project(project_name)
                if project:
                    print(f"  • {project_name}")
                    if hasattr(project, "status"):
                        print(f"    Status: {project.status}")
                    if hasattr(project, "type"):
                        print(f"    Type: {project.type}")
        else:
            print("  No projects available")
        print_section("", separator="")
        return True

    except ProjectManagementError as e:
        logger.error(f"Project management error: {str(e)}")
        print_error("Project management error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error listing projects")
        print_error("Unexpected error listing projects", exception=e)
        return False


def handle_status(args):
    """Handle orchestration status command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Getting orchestration system status")

        engine = get_orchestration_engine()
        status = engine.get_system_status()

        print_section("Orchestration System Status")
        print(format_output(status, format_type="json"))
        print_section("", separator="")
        return True

    except OrchestrationError as e:
        logger.error(f"Orchestration error: {str(e)}")
        print_error("Orchestration error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error getting status")
        print_error("Unexpected error getting status", exception=e)
        return False


def handle_health(args):
    """Handle health check command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Performing orchestration system health check")

        engine = get_orchestration_engine()
        health = engine.health_check()

        print_section("Orchestration Health Check")
        if isinstance(health, dict):
            overall = health.get("overall_status", "unknown")
            print(f"Overall Status: {overall}")
            components = health.get("components", {})
            for comp_name, comp_health in components.items():
                comp_status = comp_health.get("status", "unknown")
                status_icon = "✅" if comp_status == "healthy" else "❌"
                print(f"  {status_icon} {comp_name}: {comp_status}")
        else:
            print(format_output(health, format_type="json"))
        print_section("", separator="")
        return True

    except OrchestrationError as e:
        logger.error(f"Orchestration error: {str(e)}")
        print_error("Orchestration error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during health check")
        print_error("Unexpected error during health check", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Project Orchestration operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list-workflows
  %(prog)s run-workflow my-workflow
  %(prog)s list-projects
  %(prog)s status
  %(prog)s health
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List workflows command
    subparsers.add_parser("list-workflows", help="List available workflows")

    # Run workflow command
    run_parser = subparsers.add_parser("run-workflow", help="Run a workflow")
    run_parser.add_argument("name", help="Workflow name")

    # List projects command
    subparsers.add_parser("list-projects", help="List available projects")

    # Status command
    subparsers.add_parser("status", help="Show orchestration system status")

    # Health command
    subparsers.add_parser("health", help="Check orchestration system health")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "list-workflows": handle_list_workflows,
        "run-workflow": handle_run_workflow,
        "list-projects": handle_list_projects,
        "status": handle_status,
        "health": handle_health,
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

