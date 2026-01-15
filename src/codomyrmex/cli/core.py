import sys
import argparse
import json
import logging
from pathlib import Path

import codomyrmex.performance
from .utils import (
    get_logger,
    TerminalFormatter,
    TERMINAL_INTERFACE_AVAILABLE,
    PERFORMANCE_MONITORING_AVAILABLE,
)

# Import all handlers
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
)

# Add the src directory to Python path for development (legacy support)
src_dir = Path(__file__).parent.parent.parent
if str(src_dir) not in sys.path:
    pass

logger = get_logger(__name__)

def main():
    """Enhanced main CLI entry point with comprehensive functionality."""
    parser = argparse.ArgumentParser(
        description="Codomyrmex - Enhanced Modular Coding Workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codomyrmex check                           # Check environment setup
  codomyrmex info                            # Show project information
  codomyrmex modules                         # List all available modules
  codomyrmex status                          # Show system status dashboard
  codomyrmex shell                           # Launch interactive shell

  # Workflow Management
  codomyrmex workflow list                   # List available workflows
  codomyrmex workflow create my-workflow     # Create a new workflow
  codomyrmex workflow run ai-analysis        # Run a specific workflow

  # Project Management
  codomyrmex project list                    # List available projects
  codomyrmex project create my-project       # Create a new project
  codomyrmex project create my-project --template web_application  # Create with template

  # Orchestration System
  codomyrmex orchestration status            # Show orchestration system status
  codomyrmex orchestration health            # Check system health

  # AI Operations
  codomyrmex ai generate "create a function" # Generate code with AI
  codomyrmex ai refactor file.py "optimize"  # Refactor code with AI

  # Analysis Operations
  codomyrmex analyze code src/               # Analyze code quality
  codomyrmex analyze git --repo .            # Analyze git repository

  # Build Operations
  codomyrmex build project                   # Build the project
        """,
    )

    # Main command groups
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Global options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--performance", "-p", action="store_true", help="Enable performance monitoring"
    )

    # Environment commands
    subparsers.add_parser("check", help="Check environment setup")

    subparsers.add_parser("info", help="Show project information")

    subparsers.add_parser("modules", help="List available modules")

    subparsers.add_parser(
        "status", help="Show comprehensive system status"
    )

    subparsers.add_parser("shell", help="Launch interactive shell")

    # Workflow commands
    workflow_parser = subparsers.add_parser("workflow", help="Workflow management")
    workflow_subparsers = workflow_parser.add_subparsers(
        dest="workflow_action", help="Workflow actions"
    )

    workflow_subparsers.add_parser(
        "list", help="List available workflows"
    )

    wf_run_parser = workflow_subparsers.add_parser("run", help="Run a workflow")
    wf_run_parser.add_argument("workflow_name", help="Name of workflow to run")
    wf_run_parser.add_argument(
        "--params", "-p", type=str, help="JSON parameters for workflow"
    )
    wf_run_parser.add_argument(
        "--async", action="store_true", help="Run workflow asynchronously"
    )

    wf_create_parser = workflow_subparsers.add_parser(
        "create", help="Create a new workflow"
    )
    wf_create_parser.add_argument("name", help="Name for new workflow")
    wf_create_parser.add_argument("--template", help="Template to base workflow on")

    # Project commands
    project_parser = subparsers.add_parser("project", help="Project management")
    project_subparsers = project_parser.add_subparsers(
        dest="project_action", help="Project actions"
    )

    proj_create_parser = project_subparsers.add_parser(
        "create", help="Create a new project"
    )
    proj_create_parser.add_argument("name", help="Name for new project")
    proj_create_parser.add_argument(
        "--template", default="ai_analysis", help="Project template to use"
    )
    proj_create_parser.add_argument("--description", help="Project description")
    proj_create_parser.add_argument("--path", help="Project directory path")

    project_subparsers.add_parser(
        "list", help="List available projects"
    )

    # Orchestration commands
    orchestration_parser = subparsers.add_parser(
        "orchestration", help="Orchestration system management"
    )
    orchestration_subparsers = orchestration_parser.add_subparsers(
        dest="orchestration_action", help="Orchestration actions"
    )

    orchestration_subparsers.add_parser(
        "status", help="Show orchestration system status"
    )
    orchestration_subparsers.add_parser(
        "health", help="Check orchestration system health"
    )

    # Module-specific commands
    module_parser = subparsers.add_parser("module", help="Module-specific operations")
    module_subparsers = module_parser.add_subparsers(
        dest="module_action", help="Module actions"
    )

    mod_test_parser = module_subparsers.add_parser(
        "test", help="Test a specific module"
    )
    mod_test_parser.add_argument("module_name", help="Module to test")

    mod_demo_parser = module_subparsers.add_parser("demo", help="Run module demo")
    mod_demo_parser.add_argument("module_name", help="Module to demo")

    # AI commands
    ai_parser = subparsers.add_parser("ai", help="AI-powered operations")
    ai_subparsers = ai_parser.add_subparsers(dest="ai_action", help="AI actions")

    ai_generate_parser = ai_subparsers.add_parser("generate", help="Generate code")
    ai_generate_parser.add_argument("prompt", help="Code generation prompt")
    ai_generate_parser.add_argument(
        "--language", "-l", default="python", help="Programming language"
    )
    ai_generate_parser.add_argument("--provider", default="openai", help="LLM provider")

    ai_refactor_parser = ai_subparsers.add_parser("refactor", help="Refactor code")
    ai_refactor_parser.add_argument("file", help="File to refactor")
    ai_refactor_parser.add_argument("instruction", help="Refactoring instruction")

    # Analysis commands
    analyze_parser = subparsers.add_parser("analyze", help="Code analysis operations")
    analyze_subparsers = analyze_parser.add_subparsers(
        dest="analyze_action", help="Analysis actions"
    )

    analyze_code_parser = analyze_subparsers.add_parser(
        "code", help="Analyze code quality"
    )
    analyze_code_parser.add_argument("path", help="Path to analyze")
    analyze_code_parser.add_argument("--output", help="Output directory")

    analyze_git_parser = analyze_subparsers.add_parser(
        "git", help="Analyze git repository"
    )
    analyze_git_parser.add_argument("--repo", default=".", help="Repository path")

    # Build commands
    build_parser = subparsers.add_parser("build", help="Build and synthesis operations")
    build_subparsers = build_parser.add_subparsers(
        dest="build_action", help="Build actions"
    )

    build_project_parser = build_subparsers.add_parser("project", help="Build project")
    build_project_parser.add_argument("--config", help="Build configuration file")

    # FPF commands
    fpf_parser = subparsers.add_parser("fpf", help="First Principles Framework operations")
    fpf_subparsers = fpf_parser.add_subparsers(dest="fpf_action", help="FPF actions")

    fpf_fetch_parser = fpf_subparsers.add_parser("fetch", help="Fetch latest FPF spec from GitHub")
    fpf_fetch_parser.add_argument("--repo", default="ailev/FPF", help="GitHub repository")
    fpf_fetch_parser.add_argument("--branch", default="main", help="Branch name")
    fpf_fetch_parser.add_argument("--output", help="Output file path")

    fpf_parse_parser = fpf_subparsers.add_parser("parse", help="Parse local FPF-Spec.md")
    fpf_parse_parser.add_argument("file", help="Path to FPF-Spec.md file")
    fpf_parse_parser.add_argument("--output", help="Output JSON file path")

    fpf_export_parser = fpf_subparsers.add_parser("export", help="Export FPF to JSON")
    fpf_export_parser.add_argument("file", help="Path to FPF-Spec.md file")
    fpf_export_parser.add_argument("--output", required=True, help="Output JSON file path")
    fpf_export_parser.add_argument("--format", default="json", choices=["json"], help="Export format")

    fpf_search_parser = fpf_subparsers.add_parser("search", help="Search FPF patterns")
    fpf_search_parser.add_argument("query", help="Search query")
    fpf_search_parser.add_argument("--file", help="Path to FPF-Spec.md file")
    fpf_search_parser.add_argument("--status", help="Filter by status")
    fpf_search_parser.add_argument("--part", help="Filter by part (A, B, C, etc.)")

    fpf_visualize_parser = fpf_subparsers.add_parser("visualize", help="Generate visualizations")
    fpf_visualize_parser.add_argument("file", help="Path to FPF-Spec.md file")
    fpf_visualize_parser.add_argument("--type", choices=["hierarchy", "dependencies", "shared-terms", "concept-map", "part-hierarchy", "status-distribution"], default="hierarchy", help="Visualization type")
    fpf_visualize_parser.add_argument("--output", required=True, help="Output file path")
    fpf_visualize_parser.add_argument("--format", choices=["mermaid", "png"], default="mermaid", help="Output format")
    fpf_visualize_parser.add_argument("--layout", choices=["hierarchical", "spring", "circular"], default="hierarchical", help="Layout type (for dependency/concept-map)")
    fpf_visualize_parser.add_argument("--chart-type", choices=["bar", "pie"], default="bar", help="Chart type (for status-distribution)")

    fpf_context_parser = fpf_subparsers.add_parser("context", help="Build context for prompt engineering")
    fpf_context_parser.add_argument("file", help="Path to FPF-Spec.md file")
    fpf_context_parser.add_argument("--pattern", help="Pattern ID to build context for")
    fpf_context_parser.add_argument("--output", help="Output file path")
    fpf_context_parser.add_argument("--depth", type=int, default=1, help="Relationship depth")

    fpf_export_section_parser = fpf_subparsers.add_parser("export-section", help="Export a section (part/pattern)")
    fpf_export_section_parser.add_argument("file", help="Path to FPF-Spec.md file")
    fpf_export_section_parser.add_argument("--part", help="Part identifier to export (A, B, C, etc.)")
    fpf_export_section_parser.add_argument("--pattern", help="Pattern ID to export")
    fpf_export_section_parser.add_argument("--output", required=True, help="Output JSON file path")
    fpf_export_section_parser.add_argument("--include-dependencies", action="store_true", help="Include dependent patterns")

    fpf_analyze_parser = fpf_subparsers.add_parser("analyze", help="Analyze FPF specification")
    fpf_analyze_parser.add_argument("file", help="Path to FPF-Spec.md file")
    fpf_analyze_parser.add_argument("--output", help="Output JSON file path")

    fpf_report_parser = fpf_subparsers.add_parser("report", help="Generate comprehensive report")
    fpf_report_parser.add_argument("file", help="Path to FPF-Spec.md file")
    fpf_report_parser.add_argument("--output", required=True, help="Output HTML file path")
    fpf_report_parser.add_argument("--include-analysis", action="store_true", default=True, help="Include analysis sections")

    # Skills commands
    skills_parser = subparsers.add_parser("skills", help="Skills management operations")
    skills_subparsers = skills_parser.add_subparsers(dest="skills_action", help="Skills actions")

    skills_sync_parser = skills_subparsers.add_parser("sync", help="Sync with upstream skills repository")
    skills_sync_parser.add_argument("--force", action="store_true", help="Force re-clone even if directory exists")

    skills_list_parser = skills_subparsers.add_parser("list", help="List available skills")
    skills_list_parser.add_argument("category", nargs="?", help="Optional category filter")

    skills_get_parser = skills_subparsers.add_parser("get", help="Get a specific skill")
    skills_get_parser.add_argument("category", help="Skill category")
    skills_get_parser.add_argument("name", help="Skill name")
    skills_get_parser.add_argument("--output", help="Output file path (JSON or YAML)")

    skills_search_parser = skills_subparsers.add_parser("search", help="Search skills")
    skills_search_parser.add_argument("query", help="Search query")

    # Parse arguments
    args = parser.parse_args()

    # Initialize performance monitoring if requested
    if args.performance and PERFORMANCE_MONITORING_AVAILABLE:
        from codomyrmex.performance.performance_monitor import PerformanceMonitor
        monitor = PerformanceMonitor()
        logger.info("Performance monitoring enabled")
        codomyrmex.performance._performance_monitor = monitor

    # Set verbose logging
    if args.verbose:
        logger.setLevel(10)  # DEBUG level
        logger.debug("Verbose mode enabled")

    # Route commands
    success = True

    if args.command == "check":
        success = check_environment()
        if success:
            formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None
            msg = "Codomyrmex environment looks good! You can now use all modules and tools."
            print(f"\n{formatter.success(msg) if formatter else f'🎉 {msg}'}")
        else:
            print("\n❌ Environment setup issues detected.")
            print(
                "Please run the setup script or check the README for installation instructions."
            )
            sys.exit(1)

    elif args.command == "info":
        show_info()

    elif args.command == "modules":
        show_modules()

    elif args.command == "status":
        show_system_status()

    elif args.command == "shell":
        success = run_interactive_shell()

    elif args.command == "workflow":
        if args.workflow_action == "list":
            success = list_workflows()
        elif args.workflow_action == "run":
            params = {}
            if args.params:
                try:
                    params = json.loads(args.params)
                except json.JSONDecodeError:
                    print("❌ Invalid JSON in --params")
                    sys.exit(1)
            success = run_workflow(args.workflow_name, **params)
        elif args.workflow_action == "create":
            success = handle_workflow_create(args.name, args.template)

    elif args.command == "project":
        if args.project_action == "create":
            kwargs = {}
            if args.description:
                kwargs["description"] = args.description
            if args.path:
                kwargs["path"] = args.path
            success = handle_project_create(args.name, args.template, **kwargs)
        elif args.project_action == "list":
            success = handle_project_list()

    elif args.command == "orchestration":
        if args.orchestration_action == "status":
            success = handle_orchestration_status()
        elif args.orchestration_action == "health":
            success = handle_orchestration_health()

    elif args.command == "ai":
        if args.ai_action == "generate":
            success = handle_ai_generate(args.prompt, args.language, args.provider)
        elif args.ai_action == "refactor":
            success = handle_ai_refactor(args.file, args.instruction)

    elif args.command == "analyze":
        if args.analyze_action == "code":
            success = handle_code_analysis(args.path, args.output)
        elif args.analyze_action == "git":
            success = handle_git_analysis(args.repo)

    elif args.command == "build":
        if args.build_action == "project":
            success = handle_project_build(args.config)

    elif args.command == "module":
        if args.module_action == "test":
            success = handle_module_test(args.module_name)
        elif args.module_action == "demo":
            success = handle_module_demo(args.module_name)

    elif args.command == "fpf":
        if args.fpf_action == "fetch":
            success = handle_fpf_fetch(args.repo, args.branch, args.output)
        elif args.fpf_action == "parse":
            success = handle_fpf_parse(args.file, args.output)
        elif args.fpf_action == "export":
            success = handle_fpf_export(args.file, args.output, args.format)
        elif args.fpf_action == "search":
            filters = {}
            if args.status:
                filters["status"] = args.status
            if args.part:
                filters["part"] = args.part
            success = handle_fpf_search(args.query, args.file, filters)
        elif args.fpf_action == "visualize":
            success = handle_fpf_visualize(args.file, args.type, args.output, args.format, args.layout, args.chart_type)
        elif args.fpf_action == "context":
            success = handle_fpf_context(args.file, args.pattern, args.output, args.depth)
        elif args.fpf_action == "export-section":
            success = handle_fpf_export_section(args.file, args.part, args.pattern, args.output, args.include_dependencies)
        elif args.fpf_action == "analyze":
            success = handle_fpf_analyze(args.file, args.output)
        elif args.fpf_action == "report":
            success = handle_fpf_report(args.file, args.output, args.include_analysis)

    elif args.command == "skills":
        if args.skills_action == "sync":
            success = handle_skills_sync(args.force)
        elif args.skills_action == "list":
            success = handle_skills_list(args.category)
        elif args.skills_action == "get":
            success = handle_skills_get(args.category, args.name, args.output)
        elif args.skills_action == "search":
            success = handle_skills_search(args.query)
        else:
            skills_parser.print_help()
            success = False

    else:
        if args.command is None:
            parser.print_help()
        else:
            print(f"❌ Unknown command: {args.command}")
            success = False

    # Return success status (exit with code only if not running tests)
    if __name__ != "__main__":
        return success  # Return for testing
    else:
        sys.exit(0 if success else 1)  # Exit for normal execution

if __name__ == "__main__":
    main()
