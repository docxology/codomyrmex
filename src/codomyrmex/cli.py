#!/usr/bin/env python3
"""
Codomyrmex CLI - Command Line Interface for Codomyrmex

A modular, extensible coding workspace that integrates various tools
for building, documenting, analyzing, executing, and visualizing code.
Now with comprehensive orchestration and project management capabilities.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add the src directory to Python path for development
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    pass
#     sys.path.insert(0, str(src_dir))  # Removed sys.path manipulation

# Import core logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging

    logger = get_logger(__name__)
except ImportError:
    try:
        # Try importing from installed package
        from codomyrmex.logging_monitoring.logger_config import (
            get_logger,
            setup_logging,
        )

    except ImportError:
        # Fallback logging - should not happen in normal operation
        # This is a fallback for edge cases, but we should always use get_logger
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

# Import terminal interface for better UX
try:
    from codomyrmex.terminal_interface.interactive_shell import InteractiveShell
    from codomyrmex.terminal_interface.terminal_utils import (
        CommandRunner,
        TerminalFormatter,
    )

    TERMINAL_INTERFACE_AVAILABLE = True
except ImportError:
    TERMINAL_INTERFACE_AVAILABLE = False
    logger.warning("Terminal interface not available - using basic output")

# Import performance monitoring
try:
    from codomyrmex.performance.performance_monitor import (
        PerformanceMonitor,
        monitor_performance,
    )

    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False


def check_environment():
    """Check if the environment is properly set up."""
    formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

    if formatter:
        print(formatter.header("🔍 Codomyrmex Environment Check", "=", 60))
    else:
        print("🔍 Checking Codomyrmex environment...")

    success = True

    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (
        python_version.major == 3 and python_version.minor < 10
    ):
        msg = f"Python {python_version.major}.{python_version.minor} detected. Need Python 3.10+"
        print(formatter.error(msg) if formatter else f"❌ {msg}")
        success = False
    else:
        msg = f"Python {python_version.major}.{python_version.minor}.{python_version.micro}"
        print(formatter.success(msg) if formatter else f"✅ {msg}")

    # Check if we're in a virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        msg = "Running in virtual environment"
        print(formatter.success(msg) if formatter else f"✅ {msg}")
    else:
        msg = "Not running in virtual environment (consider using one)"
        print(formatter.warning(msg) if formatter else f"⚠️  {msg}")

    # Check core Codomyrmex modules
    core_modules = [
        ("codomyrmex.logging_monitoring", "Logging & Monitoring"),
        ("codomyrmex.environment_setup", "Environment Setup"),
        ("codomyrmex.model_context_protocol", "Model Context Protocol"),
    ]

    for module, desc in core_modules:
        try:
            __import__(module)
            msg = f"{desc} module"
            print(formatter.success(msg) if formatter else f"✅ {msg}")
        except ImportError as e:
            msg = f"{desc} module - {str(e)}"
            print(formatter.error(msg) if formatter else f"❌ {msg}")
            success = False

    # Check optional AI/LLM dependencies
    ai_deps = [
        ("openai", "OpenAI integration"),
        ("anthropic", "Anthropic Claude integration"),
        ("google.generativeai", "Google AI integration"),
    ]

    for dep, desc in ai_deps:
        try:
            __import__(dep)
            msg = f"{desc}"
            print(formatter.success(msg) if formatter else f"✅ {desc}")
        except ImportError:
            msg = f"{desc} (optional)"
            print(formatter.warning(msg) if formatter else f"⚠️  {desc} (optional)")

    # Check analysis and visualization dependencies
    analysis_deps = [
        ("matplotlib", "Data visualization"),
        ("numpy", "Numerical computing"),
        ("pandas", "Data analysis"),
        ("pytest", "Testing framework"),
        ("docker", "Code execution sandboxing"),
    ]

    for dep, desc in analysis_deps:
        try:
            __import__(dep)
            msg = f"{desc}"
            print(formatter.success(msg) if formatter else f"✅ {desc}")
        except ImportError:
            msg = f"{desc} (optional)"
            print(formatter.warning(msg) if formatter else f"⚠️  {desc} (optional)")

    return success


def show_info():
    """Show information about Codomyrmex."""
    formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

    info_text = """
🐜 Codomyrmex - A Modular, Extensible Coding Workspace

Codomyrmex provides a comprehensive suite of tools for:
• AI-enhanced code editing and generation
• Automated build and synthesis processes
• Static analysis and code quality checking
• Secure code execution in sandboxed environments
• Data visualization and plotting
• Documentation generation and management
• Git operations and version control
• Logging and monitoring across all modules
• Project management and orchestration

Available modules:
📝 ai_code_editing      - AI-powered code assistance
🔨 build_synthesis      - Build automation and code generation
📚 documentation        - Rich documentation with Docusaurus
🔍 static_analysis      - Code quality and security analysis
🏃 code - Code execution, sandboxing, review, and monitoring
📊 data_visualization   - Charts and data plotting
📦 git_operations       - Git workflow automation
📋 logging_monitoring   - Structured logging
🔗 model_context_protocol - LLM integration framework
🌱 environment_setup    - Development environment management
🎯 project_orchestration - Project management and task orchestration
⚡ performance          - Performance monitoring and optimization
🔬 system_discovery     - System introspection and capability mapping
💻 terminal_interface   - Interactive CLI and terminal utilities

Get started:
1. Run 'codomyrmex check' to verify your setup
2. Run 'codomyrmex shell' for interactive mode
3. Run 'codomyrmex workflow list' to see available workflows
4. See README.md for detailed setup instructions

For help: codomyrmex --help
"""

    if formatter:
        print(formatter.box(info_text, "Codomyrmex Information"))
    else:
        print(info_text)


def show_modules():
    """Show detailed information about available modules."""
    modules_info = {
        "Core Modules": {
            "ai_code_editing": "AI-powered code generation, editing, and refactoring using LLMs",
            "logging_monitoring": "Structured logging system with JSON output and multi-language support",
            "environment_setup": "Development environment validation and setup automation",
            "model_context_protocol": "Standardized protocol for LLM tool interactions",
        },
        "Analysis & Visualization": {
            "data_visualization": "Rich plotting with matplotlib, plotly, and mermaid diagrams",
            "static_analysis": "Code quality analysis with pylint, flake8, and security scanning",
            "pattern_matching": "Advanced pattern recognition and code structure analysis",
            "git_operations": "Advanced git workflows, GitHub integration, and repository management",
        },
        "Execution & Building": {
            "code": "Code execution, sandboxing, review, and monitoring",
            "build_synthesis": "Build automation and code synthesis pipelines",
            "documentation": "Automated documentation generation with Docusaurus",
        },
        "System & Management": {
            "project_orchestration": "Project management, task orchestration, and workflow automation",
            "performance": "Performance monitoring, caching, and optimization tools",
            "system_discovery": "System introspection and capability mapping",
            "terminal_interface": "Interactive CLI and terminal utilities",
        },
    }

    formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

    for category, modules in modules_info.items():
        if formatter:
            print(formatter.header(f"📦 {category}", "-", 50))
        else:
            print(f"\n📦 {category}")
            print("-" * 50)

        for module, description in modules.items():
            if formatter:
                print(f"  {formatter.color(module, 'BRIGHT_CYAN')}: {description}")
            else:
                print(f"  {module}: {description}")
        print()


def run_interactive_shell():
    """Launch the interactive Codomyrmex shell."""
    if not TERMINAL_INTERFACE_AVAILABLE:
        print("❌ Interactive shell requires terminal interface module")
        print("Install missing dependencies or use individual commands")
        return False

    shell = InteractiveShell()
    shell.run()
    return True


def list_workflows():
    """List available workflows and orchestration templates."""
    try:
        from codomyrmex.project_orchestration import get_workflow_manager

        manager = get_workflow_manager()
        workflows = manager.list_workflows()

        formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

        if formatter:
            print(formatter.header("🎯 Available Workflows", "=", 60))
        else:
            print("🎯 Available Workflows")
            print("=" * 60)

        if not workflows:
            print(
                "No workflows currently available. Create one with 'codomyrmex workflow create'"
            )
            return

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

    except ImportError:
        print("❌ Project orchestration module not available")
        return False
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        print(f"❌ Error listing workflows: {str(e)}")
        return False


def run_workflow(workflow_name: str, **kwargs):
    """Run a specific workflow."""
    try:
        from codomyrmex.project_orchestration import get_orchestration_engine

        engine = get_orchestration_engine()

        result = engine.execute_workflow(workflow_name, **kwargs)

        formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

        if result["success"]:
            msg = f"Workflow '{workflow_name}' completed successfully"
            print(formatter.success(msg) if formatter else f"✅ {msg}")
        else:
            msg = f"Workflow '{workflow_name}' failed: {result.get('error', 'Unknown error')}"
            print(formatter.error(msg) if formatter else f"❌ {msg}")

        return result["success"]

    except ImportError:
        print("❌ Project orchestration module not available")
        return False
    except (AttributeError, KeyError, TypeError, ValueError, RuntimeError) as e:
        print(f"❌ Error running workflow: {str(e)}")
        return False


def show_system_status():
    """Show comprehensive system status."""
    formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

    if formatter:
        print(formatter.header("🔧 System Status Dashboard", "=", 60))
    else:
        print("🔧 System Status Dashboard")
        print("=" * 60)

    # Check environment
    print("\n📋 Environment Check:")
    check_environment()

    # Check modules
    print("\n📦 Module Status:")
    modules = [
        "ai_code_editing",
        "data_visualization",
        "code",
        "git_operations",
        "build_synthesis",
        "static_analysis",
        "logging_monitoring",
        "environment_setup",
        "model_context_protocol",
    ]

    for module in modules:
        try:
            __import__(f"codomyrmex.{module}")
            msg = f"{module.replace('_', ' ').title()}"
            print(formatter.success(msg) if formatter else f"✅ {msg}")
        except ImportError:
            msg = f"{module.replace('_', ' ').title()} - Not available"
            print(formatter.error(msg) if formatter else f"❌ {msg}")

    # System discovery
    try:
        from codomyrmex.system_discovery import StatusReporter

        reporter = StatusReporter()

        print("\n🔍 System Discovery:")
        report = reporter.generate_comprehensive_report()

        for category, status in report.items():
            if isinstance(status, dict) and "status" in status:
                status_text = "✅" if status["status"] else "❌"
                print(f"  {status_text} {category.replace('_', ' ').title()}")
    except ImportError:
        print("\n🔍 System Discovery: Not available")

    # Performance monitoring
    if PERFORMANCE_MONITORING_AVAILABLE:
        try:
            monitor = PerformanceMonitor()
            stats = monitor.get_stats()
            print("\n⚡ Performance Stats:")
            print(f"  📊 Monitored functions: {len(stats.get('functions', []))}")
        except (AttributeError, KeyError, TypeError):
            # Performance monitor may not be available or stats may be incomplete
            pass


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

    # Parse arguments
    args = parser.parse_args()

    # Initialize performance monitoring if requested
    if args.performance and PERFORMANCE_MONITORING_AVAILABLE:
        monitor = PerformanceMonitor()
        logger.info("Performance monitoring enabled")

        # Enable performance monitoring globally
        import codomyrmex.performance

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


# Helper functions for command handling
def handle_ai_generate(prompt: str, language: str, provider: str) -> bool:
    """Handle AI code generation command."""
    try:
        from codomyrmex.agents.ai_code_editing import generate_code_snippet

        result = generate_code_snippet(
            prompt=prompt, language=language, provider=provider
        )

        if result["status"] == "success":
            print("Generated code:")
            print("-" * 40)
            print(result["generated_code"])
            print("-" * 40)
            return True
        else:
            print(f"❌ Code generation failed: {result['error_message']}")
            return False

    except ImportError:
        print("❌ AI code editing module not available")
        return False
    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        print(f"❌ Error generating code: {str(e)}")
        return False


def handle_ai_refactor(file_path: str, instruction: str) -> bool:
    """Handle AI code refactoring command."""
    try:
        from codomyrmex.agents.ai_code_editing import refactor_code_snippet

        # Read the file
        with open(file_path) as f:
            code = f.read()

        # Determine language from file extension
        language = Path(file_path).suffix.lstrip(".")
        if language == "py":
            language = "python"
        elif language == "js":
            language = "javascript"

        result = refactor_code_snippet(
            code_snippet=code, refactoring_instruction=instruction, language=language
        )

        if result["status"] in ["success", "no_change_needed"]:
            print("Refactored code:")
            print("-" * 40)
            print(result["refactored_code"])
            print("-" * 40)
            if result.get("explanation"):
                print(f"Explanation: {result['explanation']}")
            return True
        else:
            print(f"❌ Refactoring failed: {result['error_message']}")
            return False

    except ImportError:
        print("❌ AI code editing module not available")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except (ValueError, TypeError, AttributeError, RuntimeError, OSError) as e:
        print(f"❌ Error refactoring code: {str(e)}")
        return False


def handle_code_analysis(path: str, output_dir: Optional[str]) -> bool:
    """Handle code analysis command."""
    try:
        from codomyrmex.static_analysis import analyze_project

        result = analyze_project(path)
        print(f"Code quality analysis for: {path}")
        print(f"Quality Score: {result.get('score', 'N/A')}/10")

        if output_dir:
            output_file = Path(output_dir) / "analysis_report.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"Report saved to: {output_file}")

        return True

    except ImportError:
        print("❌ Static analysis module not available")
        return False
    except (ValueError, TypeError, AttributeError, RuntimeError, OSError, FileNotFoundError) as e:
        print(f"❌ Error analyzing code: {str(e)}")
        return False


def handle_git_analysis(repo_path: str) -> bool:
    """Handle git repository analysis command."""
    try:
        from codomyrmex.data_visualization.git_visualizer import (
            visualize_git_repository,
        )

        result = visualize_git_repository(repo_path, output_dir="./git_analysis")

        if result:
            print("✅ Git analysis complete. Check ./git_analysis/ for results.")
            return True
        else:
            print("❌ Git analysis failed")
            return False

    except ImportError:
        print("❌ Git operations or data visualization modules not available")
        return False
    except Exception as e:
        print(f"❌ Error analyzing git repository: {str(e)}")
        return False


def handle_project_build(config_file: Optional[str]) -> bool:
    """Handle project build command."""
    try:
        from codomyrmex.build_synthesis import orchestrate_build_pipeline

        build_config = {}
        if config_file and Path(config_file).exists():
            with open(config_file) as f:
                build_config = json.load(f)

        result = orchestrate_build_pipeline(build_config)

        if result.get("success"):
            print("✅ Build completed successfully")
            return True
        else:
            print(f"❌ Build failed: {result.get('error', 'Unknown error')}")
            return False

    except ImportError:
        print("❌ Build synthesis module not available")
        return False
    except Exception as e:
        print(f"❌ Error building project: {str(e)}")
        return False


def handle_module_test(module_name: str) -> bool:
    """Handle module testing command."""
    try:
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                f"src/codomyrmex/{module_name}/tests/",
                "-v",
            ],
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error testing module: {str(e)}")
        return False


def handle_module_demo(module_name: str) -> bool:
    """Handle module demo command."""
    print(f"Running demo for module: {module_name}")

    demos = {
        "data_visualization": demo_data_visualization,
        "ai_code_editing": demo_ai_code_editing,
        "code": demo_code_execution,
        "git_operations": demo_git_operations,
    }

    if module_name in demos:
        return demos[module_name]()
    else:
        print(f"❌ No demo available for module: {module_name}")
        return False


def demo_data_visualization() -> bool:
    """Demo data visualization capabilities."""
    try:
        import numpy as np

        from codomyrmex.data_visualization import create_bar_chart, create_line_plot

        # Generate sample data
        x = list(range(10))
        y = [i**2 for i in x]

        # Create visualizations
        create_line_plot(
            x, y, title="Demo: Quadratic Function", output_path="output/demo_line.png"
        )
        create_bar_chart(
            x, y, title="Demo: Bar Chart", output_path="output/demo_bar.png"
        )

        print("✅ Data visualization demo complete. Check output/ directory.")
        return True

    except ImportError:
        print("❌ Data visualization module not available")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return False


def demo_ai_code_editing() -> bool:
    """Demo AI code editing capabilities."""
    try:
        from codomyrmex.agents.ai_code_editing import generate_code_snippet

        result = generate_code_snippet(
            prompt="Create a simple function to calculate factorial", language="python"
        )

        if result["status"] == "success":
            print("✅ AI Code Generation Demo:")
            print("Generated factorial function:")
            print("-" * 40)
            print(result["generated_code"])
            print("-" * 40)
            return True
        else:
            print(f"❌ Demo failed: {result['error_message']}")
            return False

    except ImportError:
        print("❌ AI code editing module not available")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return False


def demo_code_execution() -> bool:
    """Demo code execution sandbox."""
    try:
        from codomyrmex.code import execute_code

        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(8):
    print(f"fib({i}) = {fibonacci(i)}")
"""

        result = execute_code(language="python", code=code)

        if result.get("status") == "success":
            print("✅ Code Execution Demo:")
            print("Executed Fibonacci sequence:")
            print("-" * 40)
            print(result.get("stdout", "No output"))
            print("-" * 40)
            return True
        else:
            print(f"❌ Demo failed: {result.get('error_message', result.get('stderr', 'Unknown error'))}")
            return False

    except ImportError:
        print("❌ Code execution sandbox module not available")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return False


def demo_git_operations() -> bool:
    """Demo git operations."""
    try:
        from codomyrmex.git_operations import get_current_branch, get_status

        status = get_status()
        branch = get_current_branch()

        print("✅ Git Operations Demo:")
        print(f"Current branch: {branch}")
        print(f"Repository status: {len(status.get('modified', []))} modified files")
        return True

    except ImportError:
        print("❌ Git operations module not available")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return False


# New command handlers for enhanced CLI functionality


def handle_workflow_create(name: str, template: Optional[str] = None) -> bool:
    """Handle workflow creation command."""
    try:
        from codomyrmex.project_orchestration import WorkflowStep, get_workflow_manager

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
            print(f"✅ Created workflow '{name}' with {len(steps)} steps")
            return True
        else:
            print(f"❌ Failed to create workflow '{name}'")
            return False

    except ImportError:
        print("❌ Project orchestration module not available")
        return False
    except Exception as e:
        print(f"❌ Error creating workflow: {str(e)}")
        return False


def handle_project_create(name: str, template: str = "ai_analysis", **kwargs) -> bool:
    """Handle project creation command."""
    try:
        from codomyrmex.project_orchestration import get_project_manager

        manager = get_project_manager()

        project = manager.create_project(name=name, template_name=template, **kwargs)

        print(f"✅ Created project '{name}' using template '{template}'")
        print(f"   Path: {project.path}")
        print(f"   Type: {project.type.value}")
        print(f"   Workflows: {', '.join(project.workflows)}")

        return True

    except ImportError:
        print("❌ Project orchestration module not available")
        return False
    except Exception as e:
        print(f"❌ Error creating project: {str(e)}")
        return False


def handle_project_list() -> bool:
    """Handle project listing command."""
    try:
        from codomyrmex.project_orchestration import get_project_manager

        manager = get_project_manager()
        projects = manager.list_projects()

        formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

        if formatter:
            print(formatter.header("📁 Available Projects", "=", 60))
        else:
            print("📁 Available Projects")
            print("=" * 60)

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
        print("❌ Project orchestration module not available")
        return False
    except Exception as e:
        print(f"❌ Error listing projects: {str(e)}")
        return False


def handle_orchestration_status() -> bool:
    """Handle orchestration status command."""
    try:
        from codomyrmex.project_orchestration import get_orchestration_engine

        engine = get_orchestration_engine()
        status = engine.get_system_status()

        formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

        if formatter:
            print(formatter.header("🎯 Orchestration System Status", "=", 60))
        else:
            print("🎯 Orchestration System Status")
            print("=" * 60)

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
        print("❌ Project orchestration module not available")
        return False
    except Exception as e:
        print(f"❌ Error getting orchestration status: {str(e)}")
        return False


def handle_orchestration_health() -> bool:
    """Handle orchestration health check command."""
    try:
        from codomyrmex.project_orchestration import get_orchestration_engine

        engine = get_orchestration_engine()
        health = engine.health_check()

        formatter = TerminalFormatter() if TERMINAL_INTERFACE_AVAILABLE else None

        overall_status = health.get("overall_status", "unknown")
        status_color = (
            "BRIGHT_GREEN"
            if overall_status == "healthy"
            else "YELLOW" if overall_status == "degraded" else "RED"
        )

        if formatter:
            print(formatter.header("🏥 Orchestration Health Check", "=", 60))
            print(
                f"Overall Status: {formatter.color(overall_status.upper(), status_color)}"
            )
        else:
            print("🏥 Orchestration Health Check")
            print("=" * 60)
            print(f"Overall Status: {overall_status.upper()}")

        # Component health
        components = health.get("components", {})
        for component_name, component_health in components.items():
            comp_status = component_health.get("status", "unknown")
            comp_color = (
                "BRIGHT_GREEN"
                if comp_status == "healthy"
                else "YELLOW" if comp_status == "degraded" else "RED"
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
                if formatter:
                    print(f"  {formatter.color('⚠️', 'YELLOW')} {issue}")
                else:
                    print(f"  ⚠️  {issue}")

        return overall_status in ["healthy", "degraded"]

    except ImportError:
        print("❌ Project orchestration module not available")
        return False
    except Exception as e:
        print(f"❌ Error checking orchestration health: {str(e)}")
        return False


def handle_fpf_fetch(repo: str, branch: str, output: Optional[str]) -> bool:
    """Handle FPF fetch command."""
    try:
        from codomyrmex.fpf import FPFFetcher

        fetcher = FPFFetcher()
        content = fetcher.fetch_latest(repo, branch)

        if output:
            Path(output).write_text(content, encoding="utf-8")
            print(f"✅ FPF specification fetched and saved to {output}")
        else:
            print(content)

        return True
    except Exception as e:
        print(f"❌ Error fetching FPF specification: {str(e)}")
        return False


def handle_fpf_parse(file: str, output: Optional[str]) -> bool:
    """Handle FPF parse command."""
    try:
        from codomyrmex.fpf import FPFClient

        client = FPFClient()
        spec = client.load_from_file(file)

        print(f"✅ Parsed FPF specification: {len(spec.patterns)} patterns, {len(spec.concepts)} concepts")

        if output:
            client.export_json(output)
            print(f"✅ Exported to {output}")

        return True
    except Exception as e:
        print(f"❌ Error parsing FPF specification: {str(e)}")
        return False


def handle_fpf_export(file: str, output: str, format: str) -> bool:
    """Handle FPF export command."""
    try:
        from codomyrmex.fpf import FPFClient

        client = FPFClient()
        client.load_from_file(file)
        client.export_json(output)

        print(f"✅ Exported FPF specification to {output}")
        return True
    except Exception as e:
        print(f"❌ Error exporting FPF specification: {str(e)}")
        return False


def handle_fpf_search(query: str, file: Optional[str], filters: dict) -> bool:
    """Handle FPF search command."""
    try:
        from codomyrmex.fpf import FPFClient

        if not file:
            # Try default location
            default_path = Path(__file__).parent.parent / "fpf" / "FPF-Spec.md"
            if default_path.exists():
                file = str(default_path)
            else:
                print("❌ No file specified and default not found")
                return False

        client = FPFClient()
        client.load_from_file(file)
        results = client.search(query, filters)

        print(f"Found {len(results)} matching patterns:")
        for pattern in results:
            print(f"  - {pattern.id}: {pattern.title}")

        return True
    except Exception as e:
        print(f"❌ Error searching FPF: {str(e)}")
        return False


def handle_fpf_visualize(file: str, viz_type: str, output: str, format: str, layout: str, chart_type: str) -> bool:
    """Handle FPF visualize command."""
    try:
        from codomyrmex.fpf import FPFClient, FPFVisualizer
        from codomyrmex.fpf.visualizer_png import FPFVisualizerPNG

        client = FPFClient()
        client.load_from_file(file)

        if format == "png":
            # Use PNG visualizer
            png_visualizer = FPFVisualizerPNG()
            output_path = Path(output)

            if viz_type == "shared-terms":
                png_visualizer.visualize_shared_terms_network(client.spec, output_path)
            elif viz_type == "dependencies":
                png_visualizer.visualize_pattern_dependencies(client.spec, output_path, layout=layout)
            elif viz_type == "concept-map":
                png_visualizer.visualize_concept_map(client.spec, output_path, layout=layout)
            elif viz_type == "part-hierarchy":
                png_visualizer.visualize_part_hierarchy(client.spec, output_path)
            elif viz_type == "status-distribution":
                png_visualizer.visualize_status_distribution(client.spec, output_path, chart_type=chart_type)
            else:
                # Default to hierarchy
                png_visualizer.visualize_pattern_dependencies(client.spec, output_path, layout="hierarchical")

            print(f"✅ PNG visualization saved to {output}")
        else:
            # Use Mermaid visualizer
            visualizer = FPFVisualizer()
            if viz_type == "hierarchy":
                diagram = visualizer.visualize_pattern_hierarchy(client.spec.patterns)
            else:
                diagram = visualizer.visualize_dependencies(client.spec.patterns)

            Path(output).write_text(diagram, encoding="utf-8")
            print(f"✅ Mermaid diagram saved to {output}")

        return True
    except Exception as e:
        print(f"❌ Error generating visualization: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def handle_fpf_context(file: str, pattern: Optional[str], output: Optional[str], depth: int) -> bool:
    """Handle FPF context command."""
    try:
        from codomyrmex.fpf import FPFClient

        client = FPFClient()
        client.load_from_file(file)

        if pattern:
            context = client.build_context(pattern_id=pattern)
        else:
            context = client.build_context()

        if output:
            Path(output).write_text(context, encoding="utf-8")
            print(f"✅ Context saved to {output}")
        else:
            print(context)

        return True
    except Exception as e:
        print(f"❌ Error building context: {str(e)}")
        return False


def handle_fpf_export_section(file: str, part: Optional[str], pattern: Optional[str], output: str, include_dependencies: bool) -> bool:
    """Handle FPF export-section command."""
    try:
        from codomyrmex.fpf import FPFClient
        from codomyrmex.fpf.section_manager import SectionManager
        from codomyrmex.fpf.section_exporter import SectionExporter

        client = FPFClient()
        client.load_from_file(file)

        section_manager = SectionManager(client.spec)
        exporter = SectionExporter(section_manager)

        if part:
            exporter.export_part(part, Path(output))
            print(f"✅ Part {part} exported to {output}")
        elif pattern:
            exporter.export_single_pattern(pattern, Path(output), include_related=include_dependencies)
            print(f"✅ Pattern {pattern} exported to {output}")
        else:
            print("❌ Must specify either --part or --pattern")
            return False

        return True
    except Exception as e:
        print(f"❌ Error exporting section: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def handle_fpf_analyze(file: str, output: Optional[str]) -> bool:
    """Handle FPF analyze command."""
    try:
        import json
        from codomyrmex.fpf import FPFClient
        from codomyrmex.fpf.analyzer import FPFAnalyzer

        client = FPFClient()
        client.load_from_file(file)

        analyzer = FPFAnalyzer(client.spec)
        analysis = analyzer.get_analysis_summary()

        if output:
            with open(output, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ Analysis saved to {output}")
        else:
            print(json.dumps(analysis, indent=2, default=str))

        return True
    except Exception as e:
        print(f"❌ Error analyzing FPF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def handle_fpf_report(file: str, output: str, include_analysis: bool) -> bool:
    """Handle FPF report command."""
    try:
        from codomyrmex.fpf import FPFClient
        from codomyrmex.fpf.report_generator import ReportGenerator

        client = FPFClient()
        client.load_from_file(file)

        generator = ReportGenerator(client.spec)
        generator.generate_html_report(Path(output), include_analysis=include_analysis)

        print(f"✅ Report generated at {output}")
        return True
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        setup_logging()  # Initialize logging if available
    except NameError:
        pass  # setup_logging not available
    main()
