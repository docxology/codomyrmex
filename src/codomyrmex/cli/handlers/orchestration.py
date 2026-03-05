import json
from pathlib import Path

from codomyrmex.cli.utils import (
    TERMINAL_INTERFACE_AVAILABLE,
    TerminalFormatter,
    get_logger,
    print_error,
    print_header,
    print_success,
)

logger = get_logger(__name__)


def handle_project_build(config_file: str | None) -> bool:
    """Handle project build command."""
    try:
        from codomyrmex.ci_cd_automation.build import orchestrate_build_pipeline

        build_config = {}
        if config_file and Path(config_file).exists():
            with open(config_file) as f:
                build_config = json.load(f)

        print("🚀 Starting project build pipeline...")
        result = orchestrate_build_pipeline(build_config)

        if result.get("success"):
            print_success("Build completed successfully")
            return True
        print_error(f"Build failed: {result.get('error', 'Unknown error')}")
        return False

    except ImportError:
        logger.warning("Build synthesis module not available")
        print_error("Build synthesis module not available")
        return False
    except Exception as e:
        logger.error(f"Error building project: {e}", exc_info=True)
        print_error(f"Error building project: {e!s}")
        return False


def handle_workflow_create(name: str, template: str | None = None) -> bool:
    """Handle workflow creation command."""
    try:
        from codomyrmex.logistics.orchestration.project import (
            WorkflowStep,
            get_workflow_manager,
        )

        manager = get_workflow_manager()

        # Create a simple workflow based on template
        if template == "ai-analysis":
            steps = [
                WorkflowStep(
                    name="analyze_code",
                    module="static_analysis",
                    action="analyze_code_quality",
                    parameters={"path": "."},
                ),
                WorkflowStep(
                    name="generate_insights",
                    module="ai_code_editing",
                    action="generate_code_insights",
                    parameters={"analysis_data": "{{analyze_code.output}}"},
                ),
                WorkflowStep(
                    name="create_visualization",
                    module="data_visualization",
                    action="create_analysis_chart",
                    parameters={"data": "{{generate_insights.output}}"},
                ),
            ]
        elif template == "build-and-test":
            steps = [
                WorkflowStep(
                    name="check_environment",
                    module="environment_setup",
                    action="check_environment",
                    parameters={},
                ),
                WorkflowStep(
                    name="run_tests",
                    module="code",
                    action="run_tests",
                    parameters={"test_path": "tests/"},
                ),
                WorkflowStep(
                    name="build_project",
                    module="build_synthesis",
                    action="orchestrate_build_pipeline",
                    parameters={},
                ),
            ]
        else:
            # Create a basic workflow
            steps = [
                WorkflowStep(
                    name="setup",
                    module="environment_setup",
                    action="check_environment",
                    parameters={},
                )
            ]

        success = manager.create_workflow(name, steps)

        if success:
            print_success(f"Created workflow '{name}' with {len(steps)} steps")
            return True
        print_error(f"Failed to create workflow '{name}'")
        return False

    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False
    except Exception as e:
        logger.error(f"Error creating workflow: {e}", exc_info=True)
        print_error(f"Error creating workflow: {e!s}")
        return False


def handle_project_create(name: str, template: str = "ai_analysis", **kwargs) -> bool:
    """Handle project creation command."""
    try:
        from codomyrmex.logistics.orchestration.project import get_project_manager

        manager = get_project_manager()

        project = manager.create_project(name=name, template_name=template, **kwargs)

        print_success(f"Created project '{name}' using template '{template}'")
        print(f"   Path: {project.path}")
        print(f"   Type: {project.type.value}")
        print(f"   Workflows: {', '.join(project.workflows)}")

        return True

    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False
    except Exception as e:
        logger.error(f"Error creating project: {e}", exc_info=True)
        print_error(f"Error creating project: {e!s}")
        return False


def handle_project_list() -> bool:
    """Handle project listing command."""
    try:
        from codomyrmex.logistics.orchestration.project import get_project_manager

        manager = get_project_manager()
        projects = manager.list_projects()

        formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

        print_header("📁 Available Projects")

        if not projects:
            print("No projects found. Create one with 'codomyrmex project create'")
            return True

        for project_name in projects:
            project = manager.get_project(project_name)
            if project:
                status_color = (
                    "BRIGHT_GREEN" if project.status.value == "active" else "YELLOW"
                )
                if formatter:
                    print(f"  {formatter.color(project_name, 'BRIGHT_CYAN')}")
                    print(
                        f"    Status: {formatter.color(project.status.value, status_color)}"
                    )
                    print(f"    Type: {project.type.value}")
                    print(f"    Path: {project.path}")
                else:
                    print(f"  {project_name}")
                    print(f"    Status: {project.status.value}")
                    print(f"    Type: {project.type.value}")
                    print(f"    Path: {project.path}")
                print()

        return True

    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False
    except Exception as e:
        logger.error(f"Error listing projects: {e}", exc_info=True)
        print_error(f"Error listing projects: {e!s}")
        return False


def handle_orchestration_status() -> bool:
    """Handle orchestration status command."""
    try:
        from codomyrmex.logistics.orchestration.project import get_orchestration_engine

        engine = get_orchestration_engine()
        status = engine.get_system_status()

        print_header("🎯 Orchestration System Status")

        # Active sessions
        sessions = status.get("orchestration_engine", {}).get("active_sessions", 0)
        print(f"Active Sessions: {sessions}")

        # Workflow manager status
        wf_status = status.get("workflow_manager", {})
        print(f"Total Workflows: {wf_status.get('total_workflows', 0)}")
        print(f"Running Workflows: {wf_status.get('running_workflows', 0)}")

        # Task orchestrator status
        task_status = status.get("task_orchestrator", {})
        print(f"Total Tasks: {task_status.get('total_tasks', 0)}")
        print(f"Completed Tasks: {task_status.get('completed', 0)}")
        print(f"Failed Tasks: {task_status.get('failed', 0)}")

        # Project manager status
        project_status = status.get("project_manager", {})
        print(f"Total Projects: {project_status.get('total_projects', 0)}")

        # Resource manager status
        resource_status = status.get("resource_manager", {})
        print(f"Total Resources: {resource_status.get('total_resources', 0)}")
        print(f"Active Allocations: {resource_status.get('total_allocations', 0)}")

        return True

    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False
    except Exception as e:
        logger.error(f"Error getting orchestration status: {e}", exc_info=True)
        print_error(f"Error getting orchestration status: {e!s}")
        return False


def handle_orchestration_health() -> bool:
    """Handle orchestration health check command."""
    try:
        from codomyrmex.logistics.orchestration.project import get_orchestration_engine

        engine = get_orchestration_engine()
        health = engine.health_check()

        formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

        overall_status = health.get("overall_status", "unknown")
        status_color = (
            "BRIGHT_GREEN"
            if overall_status == "healthy"
            else "YELLOW"
            if overall_status == "degraded"
            else "RED"
        )

        print_header("🏥 Orchestration Health Check")
        if formatter:
            print(
                f"Overall Status: {formatter.color(overall_status.upper(), status_color)}"
            )
        else:
            print(f"Overall Status: {overall_status.upper()}")

        # Component health
        components = health.get("components", {})
        for component_name, component_health in components.items():
            comp_status = component_health.get("status", "unknown")
            comp_color = (
                "BRIGHT_GREEN"
                if comp_status == "healthy"
                else "YELLOW"
                if comp_status == "degraded"
                else "RED"
            )

            if formatter:
                print(f"  {component_name}: {formatter.color(comp_status, comp_color)}")
            else:
                print(f"  {component_name}: {comp_status}")

        # Issues
        issues = health.get("issues", [])
        if issues:
            print(f"\nIssues Found ({len(issues)}):")
            for issue in issues:
                from codomyrmex.cli.utils import print_warning

                print_warning(issue)

        return overall_status in ["healthy", "degraded"]

    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False
    except Exception as e:
        logger.error(f"Error checking orchestration health: {e}", exc_info=True)
        print_error(f"Error checking orchestration health: {e!s}")
        return False


def list_workflows() -> bool:
    """List available workflows and orchestration templates."""
    try:
        from codomyrmex.logistics.orchestration.project import get_workflow_manager

        manager = get_workflow_manager()
        workflows = manager.list_workflows()

        formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

        print_header("🎯 Available Workflows")

        if not workflows:
            print(
                "No workflows currently available. Create one with 'codomyrmex workflow create'"
            )
            return True

        for name, info in workflows.items():
            if formatter:
                print(f"  {formatter.color(name, 'BRIGHT_GREEN')}")
                print(f"    Steps: {info['steps']}")
                print(f"    Modules: {', '.join(info['modules'])}")
                print(f"    Estimated Duration: {info['estimated_duration']}s")
            else:
                print(f"  {name}")
                print(f"    Steps: {info['steps']}")
                print(f"    Modules: {', '.join(info['modules'])}")
                print(f"    Estimated Duration: {info['estimated_duration']}s")
            print()

        return True

    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        logger.error(f"Error listing workflows: {e}", exc_info=True)
        print_error(f"Error listing workflows: {e!s}")
        return False


def run_workflow(workflow_name: str, **kwargs) -> bool:
    """Run a specific workflow."""
    try:
        from codomyrmex.logistics.orchestration.project import get_orchestration_engine

        engine = get_orchestration_engine()

        print(f"🏃 Executing workflow: {workflow_name}...")
        result = engine.execute_workflow(workflow_name, **kwargs)

        if result["success"]:
            print_success(f"Workflow '{workflow_name}' completed successfully")
        else:
            print_error(
                f"Workflow '{workflow_name}' failed: {result.get('error', 'Unknown error')}"
            )

        return result["success"]

    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False
    except (AttributeError, KeyError, TypeError, ValueError, RuntimeError) as e:
        logger.error(f"Error running workflow: {e}", exc_info=True)
        print_error(f"Error running workflow: {e!s}")
        return False
