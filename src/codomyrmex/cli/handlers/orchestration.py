"""Handlers for the ``codomyrmex workflow``, ``project``, ``orchestration`` and
``build project`` commands.

The workflow and project commands work on the current working directory, so a
later ``codomyrmex`` process started in the same directory sees what an
earlier one created:

* ``workflow create`` saves the definition to
  ``config/workflows/production/<name>.json``; ``workflow list`` and
  ``workflow run`` load every definition in that directory.
* ``project create`` scaffolds ``<name>/`` (or ``--path``) and saves
  ``project.json`` in it; ``project list`` loads ``*/project.json``.
"""

import copy
import json
from pathlib import Path
from typing import Any

from codomyrmex.cli.utils import (
    TerminalFormatter,
    print_error,
    print_header,
    print_success,
    print_warning,
)
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Step definitions (``WorkflowStep`` keyword arguments) for
# ``codomyrmex workflow create --template``. Every step calls a real codomyrmex
# function that inspects the directory the workflow runs in without changing
# its files (linters run by ``analyze_project`` may write their caches, such as
# ``.ruff_cache``). Parameters are static and passed verbatim: there is no
# ``{{step.output}}`` substitution, so steps cannot consume each other's results.
WORKFLOW_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    # Used when no template is given.
    "basic": [
        {
            "name": "validate_environment",
            "module": "environment_setup",
            "action": "validate_environment",
        },
    ],
    # Static code analysis of the current directory. The name is historical: no
    # LLM is called.
    "ai-analysis": [
        {
            "name": "list_analysis_tools",
            "module": "coding.static_analysis",
            "action": "get_available_tools",
        },
        {
            "name": "analyze_code",
            "module": "coding.static_analysis",
            "action": "analyze_project",
            "parameters": {"project_root": "."},
        },
        {
            "name": "scan_secrets",
            "module": "security",
            "action": "scan_secrets",
            "parameters": {"target_path": "."},
        },
    ],
    # Pre-build checks: environment, build toolchain, static analysis. It does
    # not run the test suite or build commands (see ``codomyrmex build project``).
    "build-and-test": [
        {
            "name": "validate_environment",
            "module": "environment_setup",
            "action": "validate_environment",
        },
        {
            "name": "check_build_environment",
            "module": "ci_cd_automation.build",
            "action": "check_build_environment",
            "dependencies": ["validate_environment"],
        },
        {
            "name": "analyze_code",
            "module": "coding.static_analysis",
            "action": "analyze_project",
            "parameters": {"project_root": "."},
            "dependencies": ["validate_environment"],
        },
    ],
}
DEFAULT_WORKFLOW_TEMPLATE = "basic"


def _cli_name(value: object, kind: str) -> str | None:
    """Return a workflow/project name given on the command line as text.

    Fire turns numeric arguments into numbers, so ``workflow create 2024``
    passes the int 2024; integers are converted back. Any other non-string
    value is reported and None is returned.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    print_error(f"Invalid {kind} name {value!r}: quote it so it is passed as text")
    return None


def _workflow_template_name(template: str | None) -> str | None:
    """Return the ``WORKFLOW_TEMPLATES`` key for ``template``, or None if unknown.

    No template selects ``basic``; underscores are accepted for hyphens.
    """
    if not template:
        return DEFAULT_WORKFLOW_TEMPLATE
    key = str(template).strip().lower().replace("_", "-")
    return key if key in WORKFLOW_TEMPLATES else None


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
        logger.error("Error building project: %s", e, exc_info=True)
        print_error(f"Error building project: {e!s}")
        return False


def handle_workflow_create(name: str, template: str | None = None) -> bool:
    """Create workflow ``name`` from a template and save it in the current directory.

    The definition is written to ``config/workflows/production/<name>.json``
    under the current working directory, where ``workflow list`` and
    ``workflow run`` load it. An existing workflow of the same name is not
    replaced.

    Args:
        name: Workflow name; also the file name, so it must start with a
            letter or digit and contain only letters, digits, ``.``, ``_``
            and ``-``.
        template: A ``WORKFLOW_TEMPLATES`` key (``basic``, ``ai-analysis``,
            ``build-and-test``; underscores are accepted for hyphens).
            Defaults to ``basic``.

    Returns:
        True if the workflow was created and saved.
    """
    checked_name = _cli_name(name, "workflow")
    if checked_name is None:
        return False
    name = checked_name
    template_name = _workflow_template_name(template)
    if template_name is None:
        print_error(f"Unknown workflow template '{template}'")
        print(
            f"   Valid templates: {', '.join(WORKFLOW_TEMPLATES)} "
            "(underscores may replace hyphens)"
        )
        return False

    try:
        from codomyrmex.logistics.orchestration.project import (
            WorkflowManager,
            WorkflowStep,
        )
    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False

    steps = [
        WorkflowStep(**copy.deepcopy(spec))
        for spec in WORKFLOW_TEMPLATES[template_name]
    ]
    try:
        manager = WorkflowManager()
        if manager.get_workflow(name) is not None:
            print_error(f"Workflow '{name}' already exists")
            print(f"   File: {manager.workflow_files.get(name, manager.config_dir)}")
            print("   Choose another name or delete that file first.")
            return False
        manager.create_workflow(name, steps, persist=True)
    except (OSError, TypeError, ValueError, NotImplementedError) as e:
        logger.error("Error creating workflow %s: %s", name, e)
        print_error(f"Failed to create workflow '{name}'")
        print(f"   {e}")
        return False

    print_success(
        f"Created workflow '{name}' from template '{template_name}' "
        f"with {len(steps)} step{'' if len(steps) == 1 else 's'}"
    )
    print(f"   Saved to: {manager.workflow_files[name]}")
    for step in steps:
        after = f" (after {', '.join(step.dependencies)})" if step.dependencies else ""
        print(f"   - {step.name}: {step.module}.{step.action}{after}")
    return True


def handle_project_create(
    name: str,
    template: str = "ai_analysis",
    description: str = "",
    path: str | None = None,
) -> bool:
    """Create and scaffold project ``name`` and save its ``project.json``.

    Args:
        name: Project name.
        template: Project type, a ``ProjectType`` value such as ``ai_analysis``
            or ``web_application``; hyphens are accepted for underscores.
        description: Project description.
        path: Project directory. Defaults to ``./<name>``. ``project list``
            only finds projects in subdirectories of the directory it is run
            from.

    Returns:
        True if the project was created.
    """
    try:
        from codomyrmex.logistics.orchestration.project import (
            ProjectManager,
            ProjectType,
        )
    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False

    checked_name = _cli_name(name, "project")
    if checked_name is None:
        return False
    name = checked_name
    type_value = str(template).strip().lower().replace("-", "_")
    valid_types = [project_type.value for project_type in ProjectType]
    if type_value not in valid_types:
        print_error(f"Unknown project template '{template}'")
        print(
            f"   Valid templates: {', '.join(valid_types)} "
            "(hyphens may replace underscores)"
        )
        return False
    project_type = ProjectType(type_value)

    manager = ProjectManager()
    existing = manager.get_project(name)
    if existing is not None:
        print_error(f"Project '{name}' already exists")
        print(f"   Path: {existing.path}")
        return False
    if not path and (Path(name).name != name or name in ("", ".", "..")):
        print_error(
            f"Invalid project name '{name}': without --path it is used as the "
            "directory name, so it must not contain path separators"
        )
        return False
    project_path = Path(path) if path else manager.projects_root / name
    if project_path.exists():
        print_error(f"Cannot create project '{name}': its directory already exists")
        print(f"   Path: {project_path}")
        return False

    project = manager.create_project(
        name=name, type=project_type, description=description, path=project_path
    )
    if project is None:
        print_error(f"Failed to create project '{name}'; see the log for the cause")
        print(f"   Path: {project_path}")
        return False

    print_success(f"Created project '{name}' using template '{project_type.value}'")
    print(f"   Path: {project.path}")
    print(f"   Type: {project.type.value}")
    print(f"   Status: {project.status.value}")
    if project.description:
        print(f"   Description: {project.description}")
    print(f"   Metadata: {project.metadata_file}")
    if project.path.resolve().parent != manager.projects_root.resolve():
        print_warning(
            "'codomyrmex project list' only finds projects in subdirectories of "
            "the directory it runs in; run it from this project's parent:"
        )
        print(f"   {project.path.resolve().parent}")
    return True


def handle_project_list() -> bool:
    """List the projects saved as ``*/project.json`` under the current directory."""
    try:
        from codomyrmex.logistics.orchestration.project import (
            ProjectManager,
            ProjectStatus,
        )
    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False

    manager = ProjectManager()
    projects = sorted(manager.list_projects(), key=lambda project: project.name)
    formatter = TerminalFormatter()

    print_header("📁 Available Projects")
    print(f"Projects directory: {manager.projects_root}")

    if not projects:
        print("No projects found. Create one with 'codomyrmex project create <name>'")
        return True

    for project in projects:
        status_color = (
            "BRIGHT_GREEN" if project.status is ProjectStatus.ACTIVE else "YELLOW"
        )
        print(f"  {formatter.color(project.name, 'BRIGHT_CYAN')}")
        print(f"    Status: {formatter.color(project.status.value, status_color)}")
        print(f"    Type: {project.type.value}")
        print(f"    Path: {project.path}")
        if project.description:
            print(f"    Description: {project.description}")
        print(f"    Updated: {project.updated_at.isoformat(timespec='seconds')}")
        print()

    return True


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
        logger.error("Error getting orchestration status: %s", e, exc_info=True)
        print_error(f"Error getting orchestration status: {e!s}")
        return False


def handle_orchestration_health() -> bool:
    """Handle orchestration health check command."""
    try:
        from codomyrmex.logistics.orchestration.project import get_orchestration_engine

        engine = get_orchestration_engine()
        health = engine.health_check()

        formatter = TerminalFormatter()

        overall_status = health.get("overall_status", "unknown")
        status_color = (
            "BRIGHT_GREEN"
            if overall_status == "healthy"
            else "YELLOW"
            if overall_status == "degraded"
            else "RED"
        )

        print_header("🏥 Orchestration Health Check")
        print(
            f"Overall Status: {formatter.color(overall_status.upper(), status_color)}"
        )

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

            print(f"  {component_name}: {formatter.color(comp_status, comp_color)}")

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
        logger.error("Error checking orchestration health: %s", e, exc_info=True)
        print_error(f"Error checking orchestration health: {e!s}")
        return False


def list_workflows() -> bool:
    """List the workflows defined in ``config/workflows/production`` under cwd."""
    try:
        from codomyrmex.logistics.orchestration.project import WorkflowManager
    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False

    manager = WorkflowManager()
    names = sorted(manager.list_workflows())
    formatter = TerminalFormatter()

    print_header("🎯 Available Workflows")
    print(f"Definitions directory: {manager.config_dir}")

    if not names:
        print("No workflows found. Create one with 'codomyrmex workflow create <name>'")
        return True

    for name in names:
        steps = manager.workflows[name]
        modules = list(dict.fromkeys(step.module for step in steps))
        print(f"  {formatter.color(name, 'BRIGHT_GREEN')}")
        print(f"    Steps: {len(steps)}")
        print(f"    Modules: {', '.join(modules) if modules else '(none)'}")
        source = manager.workflow_files.get(name)
        if source is not None:
            print(f"    File: {source}")
        print()

    return True


def run_workflow(workflow_name: str, **kwargs) -> bool:
    """Run a workflow defined in ``config/workflows/production`` under cwd.

    ``kwargs`` are merged over every step's parameters. Each step's outcome is
    printed.

    Returns:
        True if every required step completed.
    """
    try:
        from codomyrmex.logistics.orchestration.project import WorkflowManager
    except ImportError:
        logger.warning("Project orchestration module not available")
        print_error("Project orchestration module not available")
        return False

    checked_name = _cli_name(workflow_name, "workflow")
    if checked_name is None:
        return False
    workflow_name = checked_name
    manager = WorkflowManager()
    steps = manager.get_workflow(workflow_name)
    if steps is None:
        available = ", ".join(sorted(manager.list_workflows())) or "none"
        print_error(f"Workflow '{workflow_name}' not found")
        print(f"   Definitions directory: {manager.config_dir}")
        print(f"   Available: {available}")
        return False

    print(f"🏃 Executing workflow: {workflow_name}...")
    try:
        execution = manager.execute_workflow(workflow_name, **kwargs)
    except (ValueError, NotImplementedError, CodomyrmexError) as e:
        logger.error("Error running workflow %s: %s", workflow_name, e)
        print_error(f"Workflow '{workflow_name}' could not run")
        print(f"   {e}")
        return False

    for step in steps:
        result = execution.step_results[step.name]
        status = result.get("status", "unknown")
        duration = result.get("duration")
        timing = f" in {duration:.2f}s" if duration is not None else ""
        line = f"   {step.name} ({step.module}.{step.action}): {status}{timing}"
        if result.get("error"):
            line += f" - {result['error']}"
        print(line)

    if execution.success:
        print_success(f"Workflow '{workflow_name}' completed successfully")
    else:
        failed = [
            name
            for name, result in execution.step_results.items()
            if result.get("status") != "completed"
        ]
        print_error(
            f"Workflow '{workflow_name}' failed ({len(failed)} of "
            f"{len(steps)} steps did not complete)"
        )
    return execution.success
