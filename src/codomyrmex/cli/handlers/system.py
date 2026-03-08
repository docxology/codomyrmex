import os
import platform
import sys

from codomyrmex.cli.utils import (
    PERFORMANCE_MONITORING_AVAILABLE,
    TERMINAL_INTERFACE_AVAILABLE,
    TerminalFormatter,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def check_environment() -> bool:
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
        python_version.major == 3 and python_version.minor < 11
    ):
        msg = f"Python {python_version.major}.{python_version.minor} detected. Need Python 3.11+"
        print(formatter.error(msg) if formatter else f"❌ {msg}")
        success = False
    else:
        msg = f"Python {python_version.major}.{python_version.minor}.{python_version.micro} ({platform.python_implementation()})"
        print(formatter.success(msg) if formatter else f"✅ {msg}")

    # Check if we're in a virtual environment
    is_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if is_venv:
        venv_path = os.environ.get("VIRTUAL_ENV", "unknown")
        msg = f"Running in virtual environment: {venv_path}"
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
            msg = f"{desc} module - {e!s}"
            print(formatter.error(msg) if formatter else f"❌ {msg}")
            success = False

    # Check optional AI/LLM dependencies
    ai_deps = [
        ("openai", "OpenAI integration"),
        ("anthropic", "Anthropic Claude integration"),
        ("google.genai", "Google GenAI integration"),
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
        ("jsonschema", "JSON Schema validation"),
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
🏃 code                 - Code execution, sandboxing, review, and monitoring
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
    except (ImportError, AttributeError, Exception):
        print("\n🔍 System Discovery: Not available")

    # Performance monitoring
    if PERFORMANCE_MONITORING_AVAILABLE:
        try:
            from codomyrmex.performance.monitoring.performance_monitor import (
                PerformanceMonitor,
            )

            monitor = PerformanceMonitor()
            stats = monitor.get_stats()
            print("\n⚡ Performance Stats:")
            print(f"  📊 Monitored functions: {len(stats.get('functions', []))}")
        except (AttributeError, KeyError, TypeError) as e:
            logger.debug("Performance stats unavailable: %s", e)


def run_interactive_shell() -> bool:
    """Launch the interactive Codomyrmex shell."""
    if not TERMINAL_INTERFACE_AVAILABLE:
        print("❌ Interactive shell requires terminal interface module")
        print("Install missing dependencies or use individual commands")
        return False

    try:
        from codomyrmex.terminal_interface.interactive_shell import InteractiveShell

        shell = InteractiveShell()
        shell.run()
        return True
    except (ImportError, Exception) as e:
        logger.error(f"Failed to launch interactive shell: {e}")
        print(f"❌ Failed to launch interactive shell: {e}")
        return False
