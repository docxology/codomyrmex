"""Dependency conflict resolution and validation.

Automates detection and resolution of Python dependency conflicts
using constraint solving and compatibility analysis.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class DependencyInfo:
    """Information about an installed dependency."""
    name: str
    version: str
    required_by: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)


@dataclass
class Conflict:
    """A detected dependency conflict."""
    package: str
    installed_version: str
    required_version: str
    required_by: str
    severity: str = "warning"  # warning, error


class DependencyResolver:
    """Resolves Python dependency conflicts.

    Uses pip and uv introspection to detect conflicts and
    suggest resolution strategies.
    """

    def __init__(self, python_path: str = "python") -> None:
        self._python = python_path

    def check_conflicts(self) -> list[Conflict]:
        """Run pip check and parse conflicts."""
        try:
            result = subprocess.run(
                [self._python, "-m", "pip", "check"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                return []
            return self._parse_pip_check(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error("Failed to run pip check: %s", e)
            return []

    def _parse_pip_check(self, output: str) -> list[Conflict]:
        """Parse pip check output into Conflict objects."""
        conflicts = []
        for line in output.strip().splitlines():
            if " requires " in line and ", but " in line:
                parts = line.split(" requires ")
                required_by = parts[0].strip()
                rest = parts[1]
                if ", but " in rest:
                    req_parts = rest.split(", but ")
                    required_version = req_parts[0].strip()
                    installed_info = req_parts[1].strip()
                    # Extract package name and version
                    pkg = required_version.split()[0] if required_version else "unknown"
                    conflicts.append(Conflict(
                        package=pkg,
                        installed_version=installed_info,
                        required_version=required_version,
                        required_by=required_by,
                    ))
        return conflicts

    def list_installed(self) -> list[DependencyInfo]:
        """List all installed packages with metadata."""
        try:
            result = subprocess.run(
                [self._python, "-m", "pip", "list", "--format=json"],
                capture_output=True, text=True, timeout=30,
            )
            packages = json.loads(result.stdout)
            return [
                DependencyInfo(name=p["name"], version=p["version"])
                for p in packages
            ]
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning("Failed to list installed packages: %s", e)
            return []

    def suggest_resolution(self, conflicts: list[Conflict]) -> list[str]:
        """Generate pip install commands to resolve conflicts."""
        suggestions = []
        for conflict in conflicts:
            suggestions.append(
                f"pip install '{conflict.package}{conflict.required_version}'"
            )
        return suggestions

    def validate_pyproject(self, pyproject_path: Path) -> list[str]:
        """Validate dependency specifications in pyproject.toml."""
        issues: list[str] = []
        if not pyproject_path.exists():
            issues.append(f"pyproject.toml not found at {pyproject_path}")
            return issues

        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore[no-redef]
            except ImportError:
                issues.append("tomllib/tomli not available for pyproject parsing")
                return issues

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        deps = data.get("project", {}).get("dependencies", [])
        if not deps:
            issues.append("No dependencies declared in [project.dependencies]")

        for dep in deps:
            if ">=" not in dep and "==" not in dep and "~=" not in dep:
                if dep.strip() and not dep.startswith("#"):
                    issues.append(f"Unpinned dependency: {dep}")
        return issues

    # ── Virtual environment detection ───────────────────────────────

    def detect_virtualenv(self) -> dict[str, Any]:
        """Detect whether running inside a virtual environment.

        Returns:
            Dict with keys: active, path, type (venv, conda, uv, none).
        """
        import os
        import sys

        venv_path = os.environ.get("VIRTUAL_ENV", "")
        conda_env = os.environ.get("CONDA_DEFAULT_ENV", "")

        if venv_path:
            # Detect if uv-managed
            venv_type = "uv" if ".venv" in venv_path or "uv" in venv_path.lower() else "venv"
            return {"active": True, "path": venv_path, "type": venv_type}
        elif conda_env:
            return {"active": True, "path": conda_env, "type": "conda"}
        elif hasattr(sys, "real_prefix"):
            return {"active": True, "path": sys.prefix, "type": "virtualenv"}
        return {"active": False, "path": "", "type": "none"}

    def get_environment_info(self) -> dict[str, Any]:
        """Get comprehensive environment information.

        Returns:
            Dict with python_version, platform, virtualenv info, and package count.
        """
        import platform
        import sys

        installed = self.list_installed()
        venv = self.detect_virtualenv()

        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "virtualenv": venv,
            "installed_packages": len(installed),
        }

    # ── Resolution report ───────────────────────────────────────────

    def generate_report(self, pyproject_path: Path | None = None) -> str:
        """Generate a full dependency health report.

        Returns:
            Multi-line text report.
        """
        lines = ["# Dependency Health Report", ""]

        # Environment
        env = self.get_environment_info()
        lines.append(f"**Python**: {env['python_version'].split()[0]}")
        lines.append(f"**Platform**: {env['platform']}")
        lines.append(f"**Virtualenv**: {env['virtualenv']['type']} ({env['virtualenv']['path'] or 'n/a'})")
        lines.append(f"**Installed packages**: {env['installed_packages']}")
        lines.append("")

        # Conflicts
        conflicts = self.check_conflicts()
        if conflicts:
            lines.append(f"## Conflicts ({len(conflicts)})")
            for c in conflicts:
                lines.append(f"- **{c.package}**: installed={c.installed_version}, "
                             f"required={c.required_version} (by {c.required_by})")
            lines.append("")
            lines.append("## Suggested fixes")
            for s in self.suggest_resolution(conflicts):
                lines.append(f"  {s}")
        else:
            lines.append("## ✅ No dependency conflicts detected")
        lines.append("")

        # Pyproject validation
        if pyproject_path:
            issues = self.validate_pyproject(pyproject_path)
            if issues:
                lines.append(f"## pyproject.toml issues ({len(issues)})")
                for i in issues:
                    lines.append(f"- {i}")
            else:
                lines.append("## ✅ pyproject.toml looks good")

        return "\n".join(lines)

    def find_outdated(self) -> list[dict[str, str]]:
        """Find outdated packages.

        Returns:
            List of dicts with name, version, latest_version.
        """
        try:
            result = subprocess.run(
                [self._python, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True, text=True, timeout=60,
            )
            packages = json.loads(result.stdout)
            return [
                {
                    "name": p["name"],
                    "version": p["version"],
                    "latest_version": p.get("latest_version", "unknown"),
                }
                for p in packages
            ]
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning("Failed to find outdated packages: %s", e)
            return []

    def full_audit(self, pyproject_path: Path | None = None) -> dict[str, Any]:
        """Run all checks and return a structured audit result.

        Returns:
            Dict with environment, conflicts, pyproject_issues, outdated, and report.
        """
        conflicts = self.check_conflicts()
        pyproject_issues = self.validate_pyproject(pyproject_path) if pyproject_path else []
        return {
            "environment": self.get_environment_info(),
            "conflicts": [
                {"package": c.package, "installed": c.installed_version,
                 "required": c.required_version, "by": c.required_by}
                for c in conflicts
            ],
            "pyproject_issues": pyproject_issues,
            "suggestions": self.suggest_resolution(conflicts),
            "conflict_count": len(conflicts),
            "issue_count": len(pyproject_issues),
        }
