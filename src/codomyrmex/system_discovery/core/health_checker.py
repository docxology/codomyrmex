"""Health and status checking for Codomyrmex system discovery.

Provides system status dashboard output, core dependency verification,
git repository status inspection, and demo workflow execution.
"""

import importlib.metadata
import json
import re
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

import codomyrmex
from codomyrmex.coding import execute_code
from codomyrmex.data_visualization import create_line_plot
from codomyrmex.logging_monitoring import get_logger as _get_logger

# Importing this module must not configure logging; entry points do that.
logger = _get_logger(__name__)

# Leading distribution name of a PEP 508 requirement string.
_REQUIREMENT_NAME = re.compile(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def core_requirements(distribution: str = "codomyrmex") -> list[str]:
    """Return the distribution names of an installed distribution's core dependencies.

    Core dependencies are the ``[project.dependencies]`` that the installed
    distribution declares; requirements that belong to an optional extra
    (their environment marker mentions ``extra``) are left out.

    Raises:
        importlib.metadata.PackageNotFoundError: If *distribution* is not
            installed, so its declared dependencies cannot be read.
    """
    names = []
    for requirement in importlib.metadata.requires(distribution) or []:
        _, _, marker = requirement.partition(";")
        if "extra" in marker:
            continue
        match = _REQUIREMENT_NAME.match(requirement)
        if match:
            names.append(match.group(1))
    return names


def installed_versions(distributions: Iterable[str]) -> dict[str, str | None]:
    """Map each distribution name to its installed version, or ``None`` if missing."""
    versions: dict[str, str | None] = {}
    for name in distributions:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


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

    def check_core_dependencies(
        self, requirements: Iterable[str] | None = None
    ) -> None:
        """Print whether each core dependency is installed.

        Args:
            requirements: Distribution names to check. Defaults to the core
                dependencies that the installed ``codomyrmex`` distribution
                declares (see :func:`core_requirements`).
        """
        print("\nCore Dependencies:")

        if requirements is None:
            try:
                requirements = core_requirements()
            except importlib.metadata.PackageNotFoundError:
                print(
                    "   UNKNOWN codomyrmex is not installed; cannot read its dependencies"
                )
                return

        for dep, version in installed_versions(requirements).items():
            if version is None:
                print(f"   MISSING {dep}")
            else:
                print(f"   OK {dep} {version}")

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
        """Get system status as a dictionary.

        ``dependencies`` maps each core dependency that the installed
        ``codomyrmex`` distribution declares to whether it is installed.

        Raises:
            importlib.metadata.PackageNotFoundError: If the ``codomyrmex``
                distribution is not installed.
        """
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

        status["dependencies"] = {
            dep: version is not None
            for dep, version in installed_versions(core_requirements()).items()
        }

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

        except Exception as _exc:
            status["git"]["is_repo"] = False

        return status

    def run_demo_workflows(self, modules: dict, output_dir: Path | None = None) -> int:
        """Execute demonstration workflows for available modules to validate system functionality.

        Args:
            modules: Dictionary of module name to ModuleInfo instances.
            output_dir: Directory for files the demos write (the demo plot).
                Defaults to a new temporary directory, so a demo never
                writes into the current working directory.

        Returns:
            The number of demos that completed successfully.
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

                if output_dir is None:
                    output_dir = Path(tempfile.mkdtemp(prefix="codomyrmex-demo-"))
                plot_path = output_dir / "demo_plot.png"
                create_line_plot(
                    x_data=x,
                    y_data=y,
                    title="Demo: Sine Wave",
                    x_label="X",
                    y_label="sin(x)",
                    output_path=str(plot_path),
                    show_plot=False,
                )
                print(f"   Created demo plot: {plot_path}")
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

        # Code execution demo (the sandbox lives in the ``coding`` module)
        if "coding" in modules and modules["coding"].is_importable:
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
                    print(
                        f"   Code execution failed ({result.get('status')}): "
                        f"{result.get('error_message') or result.get('stderr', '').strip()}"
                    )
            except Exception as e:
                print(f"   Code execution demo failed: {e}")

        print(f"\nDemo Summary: {successful_demos} workflows completed successfully")
        return successful_demos

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
        """Export the complete system inventory to ``<project_root>/codomyrmex_inventory.json``.

        Args:
            modules: Dictionary of module name to ModuleInfo instances.
        """
        print("\nGenerating Complete System Inventory...")

        inventory = {
            "project_info": {
                "name": "Codomyrmex",
                "version": codomyrmex.__version__,
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
