"""Maintenance utilities — deprecation notice management with scanning and reporting.

Provides:
- get_module_name: extract module name from file path
- get_dependency_location: determine pyproject.toml location
- add_deprecation_notice: add deprecation header to requirements.txt
- scan_for_deprecated: find all deprecated files across the project
- DeprecationReport: aggregate reporting on deprecation status
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def get_module_name(file_path: Path) -> str:
    """Extract module name from file path."""
    match = re.search(r"codomyrmex/([^/]+)/requirements\.txt", str(file_path))
    if match:
        return match.group(1)
    return "unknown"


def get_dependency_location(module_name: str) -> str:
    """Determine where dependencies are located in pyproject.toml."""
    optional_deps = {
        "code_review", "llm", "spatial.three_d", "performance",
        "physical_management", "security", "static_analysis"
    }
    if module_name in optional_deps:
        return f"pyproject.toml [project.optional-dependencies.{module_name}]"
    return "pyproject.toml [project.dependencies]"


def add_deprecation_notice(file_path: Path) -> str:
    """Add deprecation notice to a requirements.txt file.

    Returns a status message describing what was done.
    """
    module_name = get_module_name(file_path)
    location = get_dependency_location(module_name)

    notice = f"""# DEPRECATED: This file is deprecated and will be removed in a future version.
#
# All dependencies have been consolidated into pyproject.toml as the single source of truth.
#
# To install dependencies for this module:
#   uv sync --extra {module_name}
#
# Or install all optional dependencies:
#   uv sync --all-extras
#
# This file is kept temporarily for backward compatibility but should not be modified.
# See docs/project/contributing.md for the new dependency management strategy.
#
# Migration completed: {location}
#
"""

    if not file_path.exists():
        return f"⚠ {file_path.name} does not exist"

    content = file_path.read_text(encoding="utf-8")

    if content.startswith("# DEPRECATED"):
        return f"✓ {file_path.name} already has deprecation notice"

    # Comment out original content
    lines = content.splitlines()
    commented_lines = []
    for line in lines:
        if line.strip() and not line.strip().startswith("#"):
            commented_lines.append(f"# {line}")
        else:
            commented_lines.append(line)

    new_content = notice + "\n# --- Legacy content (for reference only) ---\n"
    if commented_lines:
        new_content += "\n".join(commented_lines) + "\n"

    file_path.write_text(new_content, encoding="utf-8")
    return f"✓ Updated {file_path.name}"


# ── Scanning ────────────────────────────────────────────────────────

def scan_for_deprecated(root: Path) -> list[dict[str, Any]]:
    """Scan the project for requirements.txt files and their deprecation status.

    Args:
        root: Project root directory.

    Returns:
        List of dicts with file path, module name, and deprecation status.
    """
    codomyrmex_dir = root / "src" / "codomyrmex"
    results: list[dict[str, Any]] = []

    if not codomyrmex_dir.exists():
        return results

    for module_dir in sorted(codomyrmex_dir.iterdir()):
        if not module_dir.is_dir():
            continue
        req_file = module_dir / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text(encoding="utf-8")
            results.append({
                "module": module_dir.name,
                "file": str(req_file),
                "deprecated": content.startswith("# DEPRECATED"),
                "size_bytes": req_file.stat().st_size,
            })
    return results


@dataclass
class DeprecationReport:
    """Aggregate report on deprecation status across the project."""

    entries: list[dict[str, Any]] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total."""
        return len(self.entries)

    @property
    def deprecated_count(self) -> int:
        return sum(1 for e in self.entries if e.get("deprecated"))

    @property
    def pending_count(self) -> int:
        return self.total - self.deprecated_count

    @property
    def completion_percent(self) -> float:
        if self.total == 0:
            return 100.0
        return (self.deprecated_count / self.total) * 100

    def pending_modules(self) -> list[str]:
        return [e["module"] for e in self.entries if not e.get("deprecated")]

    def summary(self) -> dict[str, Any]:
        """Summary."""
        return {
            "total_files": self.total,
            "deprecated": self.deprecated_count,
            "pending": self.pending_count,
            "completion": f"{self.completion_percent:.0f}%",
            "pending_modules": self.pending_modules(),
        }

    def text(self) -> str:
        """Text."""
        lines = [
            f"Deprecation Report: {self.deprecated_count}/{self.total} deprecation notices applied "
            f"({self.completion_percent:.0f}%)",
        ]
        if self.pending_modules():
            lines.append(f"  Pending: {', '.join(self.pending_modules())}")
        return "\n".join(lines)


def main() -> None:
    """Main entry point: add deprecation notices to all requirements.txt files."""
    root = Path(__file__).parent.parent.parent.parent
    codomyrmex_dir = root / "src" / "codomyrmex"

    requirements_files: list[Path] = []
    for module_dir in sorted(codomyrmex_dir.iterdir()):
        if module_dir.is_dir():
            req_file = module_dir / "requirements.txt"
            if req_file.exists():
                requirements_files.append(req_file)

    print(f"Found {len(requirements_files)} requirements.txt files")
    print("Adding deprecation notices...\n")

    for req_file in requirements_files:
        result = add_deprecation_notice(req_file)
        print(f"  {result}")

    print("\n✅ All deprecation notices added!")


if __name__ == "__main__":
    main()
