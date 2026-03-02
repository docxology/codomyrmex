"""Health and status checking for Codomyrmex system discovery.

Provides system status dashboard output, core dependency verification,
git repository status inspection, and demo workflow execution.
"""

import importlib
import json
import logging
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from codomyrmex.coding import execute_code
from codomyrmex.data_visualization import create_line_plot
from codomyrmex.logging_monitoring import get_logger as _get_logger

try:
    from codomyrmex.logging_monitoring.core.logger_config import (
        get_logger,
        setup_logging,
    )

    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SystemHealthChecker:
    """Checks system health, dependency status, git state, and runs demo workflows.

    Operates on a project root directory and a set of discovered modules
    (provided externally by SystemDiscovery).
    """

    def __init__(self, project_root: Path, src_path: Path, testing_path: Path):
        """Initialize the system health checker.

        Args:
            project_root: Filesystem path to the project root directory.
            src_path: Filesystem path to the source directory.
            testing_path: Filesystem path to the testing directory.
        """
        self.project_root = project_root
        self.src_path = src_path
        self.testing_path = testing_path

    def show_status_dashboard(self) -> None:
        """Display a comprehensive system status dashboard to stdout.

        Reports Python environment details, project structure health,
        core dependency availability, and git repository status.
        """
        print("\n" + "=" * 60)
        print("   CODOMYRMEX STATUS DASHBOARD")
        print("=" * 60)

        # Python environment
        print("\nPython Environment:")
        print(f"   Version: {sys.version.split()[0]}")
        print(f"   Executable: {sys.executable}")
        print(
            f"   Virtual Environment: {'Yes' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'No'}"
        )

        # Project structure
        print("\nProject Structure:")
        print(f"   Root: {self.project_root}")
        print(f"   Source exists: {'Yes' if self.src_path.exists() else 'No'}")
        print(f"   Tests exist: {'Yes' if self.testing_path.exists() else 'No'}")
        print(
            f"   Virtual env: {'Yes' if (self.project_root / '.venv').exists() or (self.project_root / 'venv').exists() else 'No'}"
        )

        # Dependencies
        self.check_core_dependencies()

        # Git status
        self.check_git_status()

    def check_core_dependencies(self) -> None:
        """Attempt to import each core dependency and print pass/fail status."""
        print("\nCore Dependencies:")

        dep_mapping = {
            "python-dotenv": "dotenv",
            "cased-kit": "kit",
            "openai": "openai",
            "anthropic": "anthropic",
            "matplotlib": "matplotlib",
            "numpy": "numpy",
            "pytest": "pytest",
            "fastapi": "fastapi",
        }

        core_deps = list(dep_mapping.keys())

        for dep in core_deps:
            try:
                import_name = dep_mapping[dep]
                importlib.import_module(import_name)
                print(f"   OK {dep}")
            except ImportError:
                print(f"   MISSING {dep}")

    def check_git_status(self) -> None:
        """Run git commands to report repo initialization, current branch, and uncommitted changes."""
        print("\nGit Repository:")

        try:
            result = subprocess.run(
                ["git", "status"], capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                print("   Git repository initialized")

                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if branch_result.returncode == 0:
                    branch = branch_result.stdout.strip()
                    print(f"   Current branch: {branch}")

                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if status_result.returncode == 0:
                    changes = status_result.stdout.strip()
                    if changes:
                        change_count = len(changes.split("\n"))
                        print(f"   {change_count} uncommitted changes")
                    else:
                        print("   Working tree clean")
            else:
                print("   Not a git repository")

        except FileNotFoundError:
            print("   Git not found")
        except Exception as e:
            print(f"   Git error: {e}")

    def get_system_status_dict(self) -> dict[str, Any]:
        """Get system status as a dictionary."""
        status = {
            "python": {
                "version": sys.version.split()[0],
                "executable": sys.executable,
                "virtual_env": hasattr(sys, "real_prefix")
                or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix),
            },
            "project": {
                "src_exists": self.src_path.exists(),
                "tests_exist": self.testing_path.exists(),
                "venv_exists": (self.project_root / ".venv").exists()
                or (self.project_root / "venv").exists(),
            },
            "dependencies": {},
            "git": {},
        }

        dep_mapping = {
            "python-dotenv": "dotenv",
            "cased-kit": "kit",
            "openai": "openai",
            "anthropic": "anthropic",
            "matplotlib": "matplotlib",
            "numpy": "numpy",
            "pytest": "pytest",
        }

        for dep, import_name in dep_mapping.items():
            try:
                importlib.import_module(import_name)
                status["dependencies"][dep] = True
            except ImportError:
                status["dependencies"][dep] = False

        try:
            result = subprocess.run(
                ["git", "status"], capture_output=True, text=True, cwd=self.project_root
            )
            status["git"]["is_repo"] = result.returncode == 0

            if status["git"]["is_repo"]:
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if branch_result.returncode == 0:
                    status["git"]["branch"] = branch_result.stdout.strip()

                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if status_result.returncode == 0:
                    status["git"]["clean"] = not status_result.stdout.strip()

        except Exception:
            status["git"]["is_repo"] = False

        return status

    def run_demo_workflows(self, modules: dict) -> None:
        """Execute demonstration workflows for available modules to validate system functionality.

        Args:
            modules: Dictionary of module name to ModuleInfo instances.
        """
        print("\n" + "=" * 60)
        print("   CODOMYRMEX DEMO WORKFLOWS")
        print("=" * 60)

        successful_demos = 0

        # Data visualization demo
        if (
            "data_visualization" in modules
            and modules["data_visualization"].is_importable
        ):
            print("\nTesting Data Visualization...")
            try:
                x = np.linspace(0, 4 * np.pi, 100)
                y = np.sin(x)

                create_line_plot(
                    x_data=x,
                    y_data=y,
                    title="Demo: Sine Wave",
                    x_label="X",
                    y_label="sin(x)",
                    output_path="demo_plot.png",
                    show_plot=False,
                )
                print("   Created demo plot: demo_plot.png")
                successful_demos += 1
            except Exception as e:
                print(f"   Data visualization demo failed: {e}")

        # Logging demo
        if (
            "logging_monitoring" in modules
            and modules["logging_monitoring"].is_importable
        ):
            print("\nTesting Logging System...")
            try:
                demo_logger = _get_logger("demo")
                demo_logger.info("Demo logging message - system working!")
                print("   Logging system functional")
                successful_demos += 1
            except Exception as e:
                print(f"   Logging demo failed: {e}")

        # Code execution demo
        if (
            "code" in modules
            and modules["code"].is_importable
        ):
            print("\nTesting Code Execution...")
            try:
                result = execute_code(
                    language="python", code="print('Hello from Codomyrmex sandbox!')"
                )
                if result.get("exit_code") == 0:
                    print(
                        f"   Code execution successful: {result.get('stdout', '').strip()}"
                    )
                    successful_demos += 1
                else:
                    print("   Code execution returned non-zero exit code")
            except Exception as e:
                print(f"   Code execution demo failed: {e}")

        print(f"\nDemo Summary: {successful_demos} workflows completed successfully")

    def check_git_repositories(self) -> None:
        """Check git repository status and related repos."""
        print("\n" + "=" * 60)
        print("   GIT REPOSITORY STATUS")
        print("=" * 60)

        # Main repository
        print("\nMain Repository:")
        self.check_git_status()

        # Check for submodules or related repositories
        print("\nDependencies & Related Repositories:")

        gitmodules_path = self.project_root / ".gitmodules"
        if gitmodules_path.exists():
            print("   Git submodules found:")
            try:
                with open(gitmodules_path) as f:
                    content = f.read()
                    print(f"      {content}")
            except Exception as e:
                print(f"   Could not read .gitmodules: {e}")
        else:
            print("   No git submodules detected")

        # Check remote repositories
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0 and result.stdout.strip():
                print("\nRemote Repositories:")
                for line in result.stdout.strip().split("\n"):
                    print(f"   {line}")
            else:
                print("\n   No remote repositories configured")

        except Exception as e:
            print(f"\n   Could not check remotes: {e}")

    def export_full_inventory(self, modules: dict) -> None:
        """Export complete system inventory to JSON file.

        Args:
            modules: Dictionary of module name to ModuleInfo instances.
        """
        print("\nGenerating Complete System Inventory...")

        inventory = {
            "project_info": {
                "name": "Codomyrmex",
                "version": "0.1.0",
                "root_path": str(self.project_root),
                "python_version": sys.version,
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            },
            "modules": {},
            "system_status": self.get_system_status_dict(),
        }

        for name, info in modules.items():
            inventory["modules"][name] = asdict(info)

        output_file = self.project_root / "codomyrmex_inventory.json"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(inventory, f, indent=2, default=str)

            print(f"   Inventory exported to: {output_file}")
            print(f"   {len(modules)} modules documented")

            total_capabilities = sum(
                len(info.capabilities) for info in modules.values()
            )
            print(f"   {total_capabilities} capabilities cataloged")

        except Exception as e:
            print(f"   Failed to export inventory: {e}")
