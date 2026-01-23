"""
Codomyrmex CLI Module

This module provides the command-line interface for the Codomyrmex development platform.
It serves as the primary entry point for user interaction with all Codomyrmex capabilities.

Available Commands:
    codomyrmex --help          Show help and available commands
    codomyrmex check           Verify environment setup and dependencies
    codomyrmex modules         List available modules and their status
    codomyrmex status          Show system status dashboard
    codomyrmex shell           Launch interactive shell mode

    Workflow Management:
    codomyrmex workflow create     Create a new workflow definition
    codomyrmex workflow list       List available workflows
    codomyrmex workflow run        Execute a workflow

    Project Operations:
    codomyrmex project create      Initialize a new project
    codomyrmex project list        List available projects

    AI Code Operations:
    codomyrmex ai generate         Generate code with AI assistance
    codomyrmex ai refactor         Refactor existing code

    Code Analysis:
    codomyrmex analyze code        Run code analysis and linting
    codomyrmex analyze git         Analyze git history and patterns

    Build Operations:
    codomyrmex build               Build project artifacts
    codomyrmex test <module>       Run tests for a specific module

    FPF (Functional Programming Format):
    codomyrmex fpf fetch           Fetch FPF data
    codomyrmex fpf parse           Parse FPF documents
    codomyrmex fpf export          Export FPF data
    codomyrmex fpf search          Search FPF content
    codomyrmex fpf visualize       Generate FPF visualizations

    Skills Management:
    codomyrmex skills sync         Synchronize skill definitions
    codomyrmex skills list         List available skills
    codomyrmex skills get          Get skill details

Usage Examples:
    # Check environment setup
    $ codomyrmex check

    # List all available modules
    $ codomyrmex modules

    # Run analysis on a file
    $ codomyrmex analyze code src/my_module/

    # Create a new workflow
    $ codomyrmex workflow create my_workflow

Architecture:
    The CLI is built on the following components:
    - core.py: Main CLI entry point and argument parsing
    - handlers/: Command handler implementations
    - Each handler corresponds to a specific command group
"""

from .core import main
from .handlers import (
    check_environment,
    show_info,
    show_modules,
    show_system_status,
    run_interactive_shell,
    handle_workflow_create,
    list_workflows,
    run_workflow,
    handle_project_create,
    handle_project_list,
    handle_orchestration_status,
    handle_orchestration_health,
    handle_ai_generate,
    handle_ai_refactor,
    handle_code_analysis,
    handle_git_analysis,
    handle_project_build,
    handle_module_test,
    handle_module_demo,
    handle_fpf_fetch,
    handle_fpf_parse,
    handle_fpf_export,
    handle_fpf_search,
    handle_fpf_visualize,
    handle_fpf_context,
    handle_fpf_export_section,
    handle_fpf_analyze,
    handle_fpf_report,
    handle_skills_sync,
    handle_skills_list,
    handle_skills_get,
    handle_skills_search,
    # Demos
    demo_data_visualization,
    demo_ai_code_editing,
    demo_code_execution,
    demo_git_operations,
)

__all__ = [
    "main",
    "check_environment",
    "show_info",
    "show_modules",
    "show_system_status",
    "run_interactive_shell",
    "handle_workflow_create",
    "list_workflows",
    "run_workflow",
    "handle_project_create",
    "handle_project_list",
    "handle_orchestration_status",
    "handle_orchestration_health",
    "handle_ai_generate",
    "handle_ai_refactor",
    "handle_code_analysis",
    "handle_git_analysis",
    "handle_project_build",
    "handle_module_test",
    "handle_module_demo",
    "handle_fpf_fetch",
    "handle_fpf_parse",
    "handle_fpf_export",
    "handle_fpf_search",
    "handle_fpf_visualize",
    "handle_fpf_context",
    "handle_fpf_export_section",
    "handle_fpf_analyze",
    "handle_fpf_report",
    "handle_skills_sync",
    "handle_skills_list",
    "handle_skills_get",
    "handle_skills_search",
    "demo_data_visualization",
    "demo_ai_code_editing",
    "demo_code_execution",
    "demo_git_operations",
]
