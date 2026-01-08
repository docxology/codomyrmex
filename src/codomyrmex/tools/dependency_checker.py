from pathlib import Path
from typing import List, Dict, Any
import argparse
import json
import subprocess
import sys


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""
"""Main entry point and utility functions

This module provides dependency_checker functionality including:
- 8 functions: run_command, check_python_version, check_dependencies...
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
Dependency Checker Tool

Validates project dependencies and checks for vulnerabilities.
"""



def run_command(cmd: List[str]) -> tuple[bool, str, str]:
    """Run a shell command and return success status, stdout, and stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def check_python_version() -> Dict[str, Any]:
    """Check Python version requirements."""
    success, stdout, stderr = run_command([sys.executable, "--version"])

    result = {
        "current_version": "unknown",
        "meets_requirement": False,
        "status": "error"
    }

    if success:
        version_str = stdout.strip().split()[1]
        result["current_version"] = version_str

        # Check if version meets minimum requirement (3.10)
        version_parts = version_str.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])

        if major > 3 or (major == 3 and minor >= 10):
            result["meets_requirement"] = True
            result["status"] = "ok"
        else:
            result["status"] = "warning"

    return result


def check_dependencies() -> Dict[str, Any]:
    """Check if main dependencies can be imported."""
    deps = {
        "core": ["cased_kit", "python_dotenv"],
        "llm": ["openai", "anthropic", "google.generativeai"],
        "analysis": ["pylint", "flake8", "bandit"],
        "data": ["matplotlib", "seaborn", "numpy"],
        "dev": ["pytest", "black", "mypy"]
    }

    results = {}

    for category, packages in deps.items():
        results[category] = {}
        for package in packages:
            try:
                __import__(package.replace(".", "_").replace("-", "_"))
                results[category][package] = {"installed": True, "status": "ok"}
            except ImportError:
                results[category][package] = {"installed": False, "status": "missing"}

    return results


def check_security() -> Dict[str, Any]:
    """Check for security vulnerabilities in dependencies."""
    security = {
        "pip_audit_available": False,
        "safety_available": False,
        "vulnerabilities": []
    }

    # Check if security tools are available
    success, _, _ = run_command([sys.executable, "-m", "pip", "show", "pip-audit"])
    security["pip_audit_available"] = success

    success, _, _ = run_command([sys.executable, "-m", "pip", "show", "safety"])
    security["safety_available"] = success

    # Run security checks if tools are available
    if security["pip_audit_available"]:
        success, stdout, stderr = run_command([
            sys.executable, "-m", "pip-audit", "--format=json"
        ])
        if success:
            try:
                vulnerabilities = json.loads(stdout)
                security["vulnerabilities"].extend(vulnerabilities)
            except:
                pass

    return security


def check_environment() -> Dict[str, Any]:
    """Check development environment setup."""
    env = {
        "virtual_env": False,
        "uv_available": False,
        "git_available": False,
        "docker_available": False
    }

    # Check for virtual environment
    env["virtual_env"] = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    # Check for development tools
    success, _, _ = run_command(["uv", "--version"])
    env["uv_available"] = success

    success, _, _ = run_command(["git", "--version"])
    env["git_available"] = success

    success, _, _ = run_command(["docker", "--version"])
    env["docker_available"] = success

    return env


def generate_report(py_version: Dict, deps: Dict, security: Dict, env: Dict) -> str:
    """Generate a dependency report."""
    report = []
    report.append("# Codomyrmex Dependency Check Report")
    report.append("=" * 50)
    report.append("")

    # Python Version
    report.append("## Python Version")
    status_icon = "✅" if py_version["status"] == "ok" else "⚠️" if py_version["status"] == "warning" else "❌"
    report.append(f"- **Current**: {py_version['current_version']}")
    report.append(f"- **Required**: >= 3.10")
    report.append(f"- **Status**: {status_icon} {'OK' if py_version['meets_requirement'] else 'Needs update'}")
    report.append("")

    # Dependencies
    report.append("## Dependencies")
    for category, packages in deps.items():
        report.append(f"### {category.title()}")
        missing = []
        for package, info in packages.items():
            status = "✅" if info["installed"] else "❌"
            report.append(f"- {package}: {status}")
            if not info["installed"]:
                missing.append(package)

        if missing:
            report.append(f"  **Missing**: {', '.join(missing)}")
        report.append("")
    report.append("")

    # Environment
    report.append("## Development Environment")
    report.append(f"- **Virtual Environment**: {'✅' if env['virtual_env'] else '❌'}")
    report.append(f"- **UV Available**: {'✅' if env['uv_available'] else '❌'}")
    report.append(f"- **Git Available**: {'✅' if env['git_available'] else '❌'}")
    report.append(f"- **Docker Available**: {'✅' if env['docker_available'] else '❌'}")
    report.append("")

    # Security
    report.append("## Security")
    report.append(f"- **Security Tools**: {len([s for s in [security['pip_audit_available'], security['safety_available']] if s])}/2 available")
    if security["vulnerabilities"]:
        report.append(f"- **Vulnerabilities Found**: {len(security['vulnerabilities'])}")
    else:
        report.append("- **Vulnerabilities**: ✅ None found")
    report.append("")

    return "\n".join(report)


def main():
    """Main function to run dependency checks."""
    parser = argparse.ArgumentParser(description="Check Codomyrmex dependencies")
    parser.add_argument("--output", "-o", help="Output file for the report")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix missing dependencies")

    args = parser.parse_args()

    print("🔍 Checking Codomyrmex dependencies...")

    # Run checks
    py_version = check_python_version()
    deps = check_dependencies()
    security = check_security()
    env = check_environment()

    # Generate report
    report = generate_report(py_version, deps, security, env)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
    else:
        print(report)

    # Auto-fix if requested
    if args.fix:
        print("\n🔧 Attempting to fix missing dependencies...")
        fix_dependencies(deps)

    print("✅ Dependency check complete!")


def fix_dependencies(deps: Dict[str, Dict]) -> None:
    """Attempt to install missing dependencies."""
    missing_packages = []

    for category, packages in deps.items():
        for package, info in packages.items():
            if not info["installed"]:
                missing_packages.append(package)

    if missing_packages:
        print(f"Installing missing packages: {', '.join(missing_packages)}")

        # Try to install with uv if available
        success, _, _ = run_command(["uv", "--version"])
        if success:
            success, stdout, stderr = run_command([
                "uv", "add"] + missing_packages
            )
        else:
            # Fall back to pip
            success, stdout, stderr = run_command([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)

        if success:
            print("✅ Successfully installed missing dependencies")
        else:
            print(f"❌ Failed to install dependencies: {stderr}")
    else:
        print("✅ All dependencies are already installed")


if __name__ == "__main__":
    main()
