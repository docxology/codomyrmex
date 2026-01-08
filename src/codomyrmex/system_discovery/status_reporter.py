from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import json
import logging
import subprocess
import sys

import importlib

from codomyrmex.logging_monitoring.logger_config import get_logger
from codomyrmex.terminal_interface.terminal_utils import TerminalFormatter




























































#!/usr/bin/env python3
"""
"""Core functionality module

This module provides status_reporter functionality including:
- 20 functions: __init__, format_message, check_python_environment...
- 1 classes: StatusReporter

Usage:
    # Example usage here
"""
Status Reporter for Codomyrmex System Discovery

Provides detailed status reporting capabilities for the Codomyrmex ecosystem,
including health checks, dependency analysis, and system diagnostics.
"""


try:

    logger = get_logger(__name__)
except ImportError:

    logger = logging.getLogger(__name__)


class StatusReporter:
    """
    Comprehensive status reporting for the Codomyrmex system.

    Provides detailed health checks, dependency analysis, and system
    diagnostics with beautiful terminal output.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the status reporter."""
        self.project_root = project_root or Path.cwd()
        self.src_path = self.project_root / "src"

        # Import terminal formatter if available
        try:

            self.formatter = TerminalFormatter()
        except ImportError:
            self.formatter = None

    def format_message(self, message: str, msg_type: str = "info") -> str:
        """Format message with colors if formatter available."""
        if not self.formatter:
            return message

        if msg_type == "success":
            return self.formatter.success(message)
        elif msg_type == "error":
            return self.formatter.error(message)
        elif msg_type == "warning":
            return self.formatter.warning(message)
        else:
            return self.formatter.info(message)

    def check_python_environment(self) -> dict[str, Any]:
        """Check Python environment status."""
        status = {
            "version": sys.version_info,
            "version_string": sys.version.split()[0],
            "executable": sys.executable,
            "virtual_env": self._in_virtual_env(),
            "path": sys.path[:5],  # First 5 path entries
            "platform": sys.platform,
        }

        return status

    def _in_virtual_env(self) -> bool:
        """Check if running in virtual environment."""
        return hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

    def check_project_structure(self) -> dict[str, Any]:
        """Check project directory structure."""
        status = {
            "project_root_exists": self.project_root.exists(),
            "src_exists": self.src_path.exists(),
            "codomyrmex_package": (self.src_path / "codomyrmex").exists(),
            "testing_dir": (self.project_root / "testing").exists(),
            "docs_dir": (
                self.project_root / "src" / "codomyrmex" / "documentation"
            ).exists(),
            "virtual_env_dir": self._check_virtual_env_dir(),
            "config_files": self._check_config_files(),
        }

        return status

    def _check_virtual_env_dir(self) -> bool:
        """Check if virtual environment directory exists."""
        venv_candidates = [".venv", "venv", "env"]
        return any(
            (self.project_root / candidate).exists() for candidate in venv_candidates
        )

    def _check_config_files(self) -> dict[str, bool]:
        """Check for important configuration files."""
        config_files = {
            "pyproject.toml": (self.project_root / "pyproject.toml").exists(),
            "requirements.txt": (self.project_root / "requirements.txt").exists(),
            "setup.py": (self.project_root / "setup.py").exists(),
            ".env": (self.project_root / ".env").exists(),
            "pytest.ini": (self.project_root / "pytest.ini").exists(),
            "README.md": (self.project_root / "README.md").exists(),
        }
        return config_files

    def check_dependencies(self) -> dict[str, Any]:
        """Check core dependencies status."""
        dependencies = {
            # Core dependencies
            "python-dotenv": self._check_import("dotenv"),
            "cased-kit": self._check_import("kit"),
            # LLM providers
            "openai": self._check_import("openai"),
            "anthropic": self._check_import("anthropic"),
            "google-generativeai": self._check_import("google.generativeai"),
            # Data science
            "numpy": self._check_import("numpy"),
            "matplotlib": self._check_import("matplotlib"),
            "pandas": self._check_import("pandas"),
            # Development tools
            "pytest": self._check_import("pytest"),
            "pylint": self._check_import("pylint"),
            "black": self._check_import("black"),
            "mypy": self._check_import("mypy"),
            # Web framework
            "fastapi": self._check_import("fastapi"),
            "uvicorn": self._check_import("uvicorn"),
        }

        # Count status
        available = sum(1 for status in dependencies.values() if status)
        total = len(dependencies)

        return {
            "dependencies": dependencies,
            "available_count": available,
            "total_count": total,
            "success_rate": (available / total) * 100 if total > 0 else 0,
        }

    def _check_import(self, module_name: str) -> bool:
        """Check if a module can be imported."""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False

    def check_git_status(self) -> dict[str, Any]:
        """Check git repository status."""
        status = {
            "is_git_repo": False,
            "git_available": False,
            "current_branch": None,
            "clean_working_tree": False,
            "remotes": [],
            "recent_commits": [],
            "staged_changes": 0,
            "unstaged_changes": 0,
        }

        # Check if git is available
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=10
            )
            status["git_available"] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return status

        if not status["git_available"]:
            return status

        # Check if we're in a git repository
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                status["is_git_repo"] = True
                status["clean_working_tree"] = not result.stdout.strip()

                # Count changes
                lines = (
                    result.stdout.strip().split("\n") if result.stdout.strip() else []
                )
                status["staged_changes"] = sum(
                    1 for line in lines if line.startswith(("A ", "M ", "D "))
                )
                status["unstaged_changes"] = sum(
                    1 for line in lines if line.endswith(("M", "D", "??"))
                )

        except subprocess.TimeoutExpired:
            pass

        if not status["is_git_repo"]:
            return status

        # Get current branch
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                status["current_branch"] = result.stdout.strip()
        except subprocess.TimeoutExpired:
            pass

        # Get remotes
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                status["remotes"] = [
                    line.strip() for line in result.stdout.split("\n") if line.strip()
                ]
        except subprocess.TimeoutExpired:
            pass

        # Get recent commits
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                status["recent_commits"] = [
                    line.strip() for line in result.stdout.split("\n") if line.strip()
                ]
        except subprocess.TimeoutExpired:
            pass

        return status

    def check_external_tools(self) -> dict[str, bool]:
        """Check availability of external tools."""
        tools = {
            "git": False,
            "npm": False,
            "node": False,
            "docker": False,
            "uv": False,
        }

        for tool in tools.keys():
            try:
                result = subprocess.run(
                    [tool, "--version"], capture_output=True, text=True, timeout=5
                )
                tools[tool] = result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                tools[tool] = False

        return tools

    def generate_comprehensive_report(self) -> dict[str, Any]:
        """Generate comprehensive system status report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "python_environment": self.check_python_environment(),
            "project_structure": self.check_project_structure(),
            "dependencies": self.check_dependencies(),
            "git_status": self.check_git_status(),
            "external_tools": self.check_external_tools(),
        }

        return report

    def display_status_report(self) -> None:
        """Display comprehensive status report with formatting."""
        report = self.generate_comprehensive_report()

        print("\n" + "=" * 70)
        print("  CODOMYRMEX SYSTEM STATUS REPORT")
        print("=" * 70)

        # Python Environment
        self._display_python_status(report["python_environment"])

        # Project Structure
        self._display_project_structure(report["project_structure"])

        # Dependencies
        self._display_dependencies_status(report["dependencies"])

        # Git Status
        self._display_git_status(report["git_status"])

        # External Tools
        self._display_external_tools(report["external_tools"])

        # Summary
        self._display_summary(report)

    def _display_python_status(self, env_status: dict[str, Any]) -> None:
        """Display Python environment status."""
        print("\n🐍 Python Environment:")
        print(f"   Version: {env_status['version_string']}")
        print(f"   Executable: {env_status['executable']}")

        if env_status["virtual_env"]:
            print(self.format_message("   Virtual Environment: Active", "success"))
        else:
            print(
                self.format_message("   Virtual Environment: Not detected", "warning")
            )

        print(f"   Platform: {env_status['platform']}")

    def _display_project_structure(self, structure: dict[str, Any]) -> None:
        """Display project structure status."""
        print("\n📂 Project Structure:")

        status_items = [
            ("Project Root", structure["project_root_exists"]),
            ("Source Directory", structure["src_exists"]),
            ("Codomyrmex Package", structure["codomyrmex_package"]),
            ("Testing Directory", structure["testing_dir"]),
            ("Documentation", structure["docs_dir"]),
            ("Virtual Environment Dir", structure["virtual_env_dir"]),
        ]

        for name, exists in status_items:
            status = (
                self.format_message("✅", "success")
                if exists
                else self.format_message("❌", "error")
            )
            print(f"   {status} {name}")

        # Config files
        print("\n📄 Configuration Files:")
        for file_name, exists in structure["config_files"].items():
            status = (
                self.format_message("✅", "success")
                if exists
                else self.format_message("❌", "error")
            )
            print(f"   {status} {file_name}")

    def _display_dependencies_status(self, deps: dict[str, Any]) -> None:
        """Display dependencies status."""
        print("\n📦 Dependencies:")
        print(
            f"   Available: {deps['available_count']}/{deps['total_count']} ({deps['success_rate']:.1f}%)"
        )

        # Group dependencies
        core_deps = ["python-dotenv", "cased-kit"]
        llm_deps = ["openai", "anthropic", "google-generativeai"]
        data_deps = ["numpy", "matplotlib", "pandas"]
        dev_deps = ["pytest", "pylint", "black", "mypy"]
        web_deps = ["fastapi", "uvicorn"]

        groups = [
            ("Core", core_deps),
            ("LLM Providers", llm_deps),
            ("Data Science", data_deps),
            ("Development", dev_deps),
            ("Web Framework", web_deps),
        ]

        for group_name, dep_list in groups:
            print(f"\n   📋 {group_name}:")
            for dep in dep_list:
                if dep in deps["dependencies"]:
                    available = deps["dependencies"][dep]
                    status = (
                        self.format_message("✅", "success")
                        if available
                        else self.format_message("❌", "error")
                    )
                    print(f"      {status} {dep}")

    def _display_git_status(self, git: dict[str, Any]) -> None:
        """Display git status."""
        print("\n🌐 Git Repository:")

        if not git["git_available"]:
            print(self.format_message("   ❌ Git not available", "error"))
            return

        if not git["is_git_repo"]:
            print(self.format_message("   ❌ Not a git repository", "error"))
            return

        print(self.format_message("   ✅ Git repository initialized", "success"))

        if git["current_branch"]:
            print(f"   🌿 Current branch: {git['current_branch']}")

        if git["clean_working_tree"]:
            print(self.format_message("   ✅ Working tree clean", "success"))
        else:
            print(
                self.format_message(
                    f"   ⚠️  {git['staged_changes']} staged, {git['unstaged_changes']} unstaged changes",
                    "warning",
                )
            )

        if git["remotes"]:
            print(f"   🌍 Remotes: {len(git['remotes'])} configured")

        if git["recent_commits"]:
            print("   📝 Recent commits:")
            for commit in git["recent_commits"][:3]:
                print(f"      • {commit}")

    def _display_external_tools(self, tools: dict[str, bool]) -> None:
        """Display external tools status."""
        print("\n🔧 External Tools:")

        for tool, available in tools.items():
            status = (
                self.format_message("✅", "success")
                if available
                else self.format_message("❌", "error")
            )
            print(f"   {status} {tool}")

    def _display_summary(self, report: dict[str, Any]) -> None:
        """Display summary and recommendations."""
        print("\n📊 Summary:")

        # Calculate overall health score
        checks = [
            report["python_environment"]["virtual_env"],
            report["project_structure"]["src_exists"],
            report["project_structure"]["codomyrmex_package"],
            report["dependencies"]["success_rate"] > 80,
            report["git_status"]["is_git_repo"],
            any(report["external_tools"].values()),
        ]

        health_score = (sum(checks) / len(checks)) * 100

        if health_score >= 90:
            health_status = self.format_message("Excellent", "success")
        elif health_score >= 70:
            health_status = self.format_message("Good", "success")
        elif health_score >= 50:
            health_status = self.format_message("Fair", "warning")
        else:
            health_status = self.format_message("Needs Attention", "error")

        print(f"   Overall Health: {health_status} ({health_score:.1f}%)")

        # Recommendations
        recommendations = []

        if not report["python_environment"]["virtual_env"]:
            recommendations.append("Create and activate a virtual environment")

        if report["dependencies"]["success_rate"] < 80:
            recommendations.append(
                "Install missing dependencies: pip install -r requirements.txt"
            )

        if not report["git_status"]["is_git_repo"]:
            recommendations.append("Initialize git repository: git init")

        if not report["external_tools"]["docker"]:
            recommendations.append("Install Docker for code execution sandbox")

        if recommendations:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")

    def export_report(self, filename: Optional[str] = None) -> str:
        """Export comprehensive report to JSON file."""
        report = self.generate_comprehensive_report()

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"codomyrmex_status_report_{timestamp}.json"

        output_path = self.project_root / filename

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)

            print(
                self.format_message(
                    f"Status report exported to: {output_path}", "success"
                )
            )
            return str(output_path)

        except Exception as e:
            print(self.format_message(f"Failed to export report: {e}", "error"))
            return ""


if __name__ == "__main__":
    # Demo the status reporter
    reporter = StatusReporter()
    reporter.display_status_report()
