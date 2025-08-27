#!/usr/bin/env python3
"""
Codomyrmex CLI - Command Line Interface for Codomyrmex

A modular, extensible coding workspace that integrates various tools
for building, documenting, analyzing, executing, and visualizing code.
"""

import sys
import os
from pathlib import Path
from typing import Optional
import argparse

# Add the code directory to Python path
code_dir = Path(__file__).parent / "code"
if str(code_dir) not in sys.path:
    sys.path.insert(0, str(code_dir))

try:
    from logging_monitoring.logger_config import get_logger, setup_logging
    logger = get_logger(__name__)
except ImportError:
    # Fallback logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

def check_environment():
    """Check if the environment is properly set up."""
    print("🔍 Checking Codomyrmex environment...")

    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print(f"❌ Python {python_version.major}.{python_version.minor} detected. Need Python 3.9+")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment (consider using one)")

    # Check core dependencies
    try:
        import dotenv
        print("✅ python-dotenv available")
    except ImportError:
        print("❌ python-dotenv not found")
        return False

    try:
        import kit
        print("✅ cased/kit available")
    except ImportError:
        print("❌ cased/kit not found")
        return False

    # Check optional dependencies
    optional_deps = [
        ('openai', 'OpenAI integration'),
        ('anthropic', 'Anthropic Claude integration'),
        ('matplotlib', 'Data visualization'),
        ('numpy', 'Numerical computing'),
        ('pytest', 'Testing framework'),
    ]

    for dep, desc in optional_deps:
        try:
            __import__(dep)
            print(f"✅ {desc}")
        except ImportError:
            print(f"⚠️  {desc} (optional)")

    return True

def show_info():
    """Show information about Codomyrmex."""
    print("""
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

Available modules:
📝 ai_code_editing      - AI-powered code assistance
🔨 build_synthesis      - Build automation and code generation
📚 documentation        - Rich documentation with Docusaurus
🔍 static_analysis      - Code quality and security analysis
🏃 code_execution_sandbox - Safe code execution
📊 data_visualization   - Charts and data plotting
📦 git_operations       - Git workflow automation
📋 logging_monitoring   - Structured logging
🔗 model_context_protocol - LLM integration framework
🌱 environment_setup    - Development environment management

Get started:
1. Run 'python codomyrmex_cli.py check' to verify your setup
2. See README.md for detailed setup instructions
3. Explore individual module documentation

For help: python codomyrmex_cli.py --help
""")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Codomyrmex - A Modular, Extensible Coding Workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python codomyrmex_cli.py check    # Check environment setup
  python codomyrmex_cli.py info     # Show project information
        """
    )

    parser.add_argument('command', choices=['check', 'info'], help='Command to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if args.command == 'check':
        success = check_environment()
        if success:
            print("\n🎉 Codomyrmex environment looks good!")
            print("You can now use the various modules and tools.")
        else:
            print("\n❌ Environment setup issues detected.")
            print("Please run the setup script or check the README for installation instructions.")
            sys.exit(1)

    elif args.command == 'info':
        show_info()

if __name__ == '__main__':
    setup_logging()  # Initialize logging if available
    main()




