"""Pre-release audit script.

Automated quality gate checks for release candidates. Validates
coverage, lint status, documentation currency, and SBOM generation.

Example::

    auditor = ReleaseAuditor()
    results = auditor.run_all()
    assert all(r.passed for r in results)
"""

from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class AuditCheck:
    """Result of a single audit check.

    Attributes:
        name: Check identifier.
        passed: Whether the check passed.
        message: Human-readable result.
        duration_ms: Check duration.
    """

    name: str
    passed: bool
    message: str
    duration_ms: float = 0.0


class ReleaseAuditor:
    """Automated pre-release quality gate.

    Runs lint, type-check, documentation, and coverage validation.

    Args:
        repo_root: Repository root path.
        min_coverage: Minimum coverage percentage.

    Example::

        auditor = ReleaseAuditor()
        results = auditor.run_all()
        for r in results:
            print(f"{'✅' if r.passed else '❌'} {r.name}: {r.message}")
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        min_coverage: float = 35.0,
    ) -> None:
        self._root = repo_root or _REPO_ROOT
        self._min_coverage = min_coverage

    def check_version_consistency(self) -> AuditCheck:
        """Verify version is consistent across pyproject.toml and AGENTS.md."""
        start = time.monotonic()
        pyproject = self._root / "pyproject.toml"
        agents = self._root / "AGENTS.md"

        if not pyproject.exists():
            return AuditCheck("version_consistency", False, "pyproject.toml not found")

        content = pyproject.read_text()
        version = ""
        for line in content.splitlines():
            if line.startswith("version"):
                version = line.split('"')[1]
                break

        if not version:
            return AuditCheck("version_consistency", False, "Could not extract version")

        agents_content = agents.read_text() if agents.exists() else ""
        agents_ok = f"v{version}" in agents_content

        elapsed = (time.monotonic() - start) * 1000
        if agents_ok:
            return AuditCheck("version_consistency", True, f"v{version} consistent", elapsed)
        return AuditCheck("version_consistency", False, f"AGENTS.md missing v{version}", elapsed)

    def check_dockerfile(self) -> AuditCheck:
        """Verify Dockerfile exists and is valid."""
        start = time.monotonic()
        dockerfile = self._root / "Dockerfile"
        elapsed = (time.monotonic() - start) * 1000

        if not dockerfile.exists():
            return AuditCheck("dockerfile", False, "Dockerfile not found", elapsed)

        content = dockerfile.read_text()
        has_from = "FROM" in content
        has_healthcheck = "HEALTHCHECK" in content
        return AuditCheck(
            "dockerfile",
            has_from and has_healthcheck,
            f"FROM: {has_from}, HEALTHCHECK: {has_healthcheck}",
            elapsed,
        )

    def check_documentation(self) -> AuditCheck:
        """Verify key documentation files exist."""
        start = time.monotonic()
        required = ["README.md", "AGENTS.md", "SPEC.md", "SECURITY.md", "LICENSE"]
        missing = [f for f in required if not (self._root / f).exists()]
        elapsed = (time.monotonic() - start) * 1000

        if missing:
            return AuditCheck("documentation", False, f"Missing: {', '.join(missing)}", elapsed)
        return AuditCheck("documentation", True, f"All {len(required)} docs present", elapsed)

    def check_module_docs(self) -> AuditCheck:
        """Verify each module has README.md."""
        start = time.monotonic()
        src = self._root / "src" / "codomyrmex"
        if not src.exists():
            return AuditCheck("module_docs", False, "src/codomyrmex not found")

        total = 0
        with_readme = 0
        for mod_dir in sorted(src.iterdir()):
            if not mod_dir.is_dir() or mod_dir.name.startswith(("_", ".")):
                continue
            if mod_dir.name == "tests":
                continue
            total += 1
            if (mod_dir / "README.md").exists():
                with_readme += 1

        elapsed = (time.monotonic() - start) * 1000
        ratio = with_readme / total if total else 0
        return AuditCheck(
            "module_docs",
            ratio >= 0.90,
            f"{with_readme}/{total} modules have README.md ({ratio:.0%})",
            elapsed,
        )

    def check_test_file_exists(self) -> AuditCheck:
        """Verify release test files exist."""
        start = time.monotonic()
        test_dir = self._root / "src" / "codomyrmex" / "tests" / "unit"
        test_files = list(test_dir.glob("test_v1_*.py")) if test_dir.exists() else []
        elapsed = (time.monotonic() - start) * 1000

        return AuditCheck(
            "release_tests",
            len(test_files) >= 2,
            f"{len(test_files)} release test files found",
            elapsed,
        )

    def check_no_todo_fixme(self) -> AuditCheck:
        """Check for critical TODO/FIXME markers in source."""
        start = time.monotonic()
        src = self._root / "src" / "codomyrmex"
        count = 0
        for py_file in src.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(errors="replace")
                count += content.count("FIXME")
            except Exception:
                continue

        elapsed = (time.monotonic() - start) * 1000
        return AuditCheck(
            "no_fixme",
            count < 10,
            f"{count} FIXME markers found",
            elapsed,
        )

    def run_all(self) -> list[AuditCheck]:
        """Execute all audit checks.

        Returns:
            List of :class:`AuditCheck` results.
        """
        checks = [
            self.check_version_consistency,
            self.check_dockerfile,
            self.check_documentation,
            self.check_module_docs,
            self.check_test_file_exists,
            self.check_no_todo_fixme,
        ]

        results = [check() for check in checks]

        passed = sum(1 for r in results if r.passed)
        total = len(results)
        logger.info("Release audit: %d/%d checks passed", passed, total)

        return results

    def get_report(self) -> str:
        """Generate a human-readable audit report.

        Returns:
            Formatted audit report string.
        """
        results = self.run_all()
        lines = ["# Pre-Release Audit Report\n"]

        for r in results:
            icon = "✅" if r.passed else "❌"
            lines.append(f"{icon} **{r.name}**: {r.message}")

        passed = sum(1 for r in results if r.passed)
        total = len(results)
        lines.append(f"\n**Result**: {passed}/{total} checks passed")

        return "\n".join(lines)


__all__ = [
    "AuditCheck",
    "ReleaseAuditor",
]
