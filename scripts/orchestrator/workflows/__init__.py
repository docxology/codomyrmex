"""Composable workflow scripts for thin orchestration.

Available workflows:
- analyze_and_report: Full codebase analysis with HTML report
- build_and_validate: Complete build pipeline with linting, type checking, tests
- quick_test: Fast parallel test runner
- module_health: Module health check workflow
- dependency_check: Check and analyze project dependencies
- code_quality: Comprehensive code quality analysis
- deploy_preview: Deploy to preview/staging environment
- parallel_tests: Run tests in parallel with coverage

Usage:
    # Run any workflow directly
    python scripts/orchestrator/workflows/build_and_validate.py --verbose

    # Use thin orchestration APIs
    from codomyrmex.orchestrator import run, pipe, batch, workflow

    # Quick commands
    result = run("scripts/orchestrator/workflows/quick_test.py")

    # Build custom workflow
    w = workflow("my_workflow")
    w.add("step1", my_action)
    w.add("step2", another_action)
    await w.run()
"""

from pathlib import Path

WORKFLOWS_DIR = Path(__file__).parent

# Available workflow scripts
WORKFLOWS = {
    "analyze_and_report": WORKFLOWS_DIR / "analyze_and_report.py",
    "build_and_validate": WORKFLOWS_DIR / "build_and_validate.py",
    "quick_test": WORKFLOWS_DIR / "quick_test.py",
    "module_health": WORKFLOWS_DIR / "module_health.py",
    "dependency_check": WORKFLOWS_DIR / "dependency_check.py",
    "code_quality": WORKFLOWS_DIR / "code_quality.py",
    "deploy_preview": WORKFLOWS_DIR / "deploy_preview.py",
    "parallel_tests": WORKFLOWS_DIR / "parallel_tests.py",
}


def list_workflows() -> dict:
    """List all available workflows.

    Returns:
        Dictionary of workflow names to paths
    """
    return {name: path for name, path in WORKFLOWS.items() if path.exists()}


def get_workflow(name: str) -> Path:
    """Get workflow path by name.

    Args:
        name: Workflow name

    Returns:
        Path to workflow script

    Raises:
        ValueError: If workflow not found
    """
    if name not in WORKFLOWS:
        available = ", ".join(WORKFLOWS.keys())
        raise ValueError(f"Unknown workflow: {name}. Available: {available}")
    return WORKFLOWS[name]


__all__ = [
    "WORKFLOWS_DIR",
    "WORKFLOWS",
    "list_workflows",
    "get_workflow",
]
