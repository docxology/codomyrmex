"""Dependency conflict resolution and validation.

Automates detection and resolution of Python dependency conflicts
using constraint solving and compatibility analysis.
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


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
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
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
