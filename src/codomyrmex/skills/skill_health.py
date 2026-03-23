"""Skill health checker — validates skill directory structure.

Scans skill directories for required files (SKILL.md, __init__.py),
optional resources, and reports health status.

Example::

    checker = SkillHealthChecker()
    report = checker.check_all()
    for skill in report["skills"]:
        print(f"  {skill['name']}: {skill['health']}")
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SKILLS_ROOT = Path(__file__).resolve().parent


@dataclass
class SkillHealth:
    """Health status of a single skill.

    Attributes:
        name: Skill name.
        path: Absolute path.
        has_skill_md: Whether SKILL.md exists.
        has_init: Whether __init__.py exists.
        has_scripts: Whether scripts/ directory exists.
        has_examples: Whether examples/ directory exists.
        has_tests: Whether test files exist.
        file_count: Number of files in the skill.
    """

    name: str
    path: str
    has_skill_md: bool = False
    has_init: bool = False
    has_scripts: bool = False
    has_examples: bool = False
    has_tests: bool = False
    file_count: int = 0

    @property
    def health(self) -> str:
        """Skill health: ``complete``, ``functional``, or ``stub``."""
        if self.has_skill_md and self.has_init:
            return "complete" if self.has_tests or self.has_examples else "functional"
        if self.has_init or self.has_skill_md:
            return "functional"
        return "stub"

    @property
    def completeness(self) -> float:
        """Completeness ratio (0.0–1.0)."""
        checks = [
            self.has_skill_md,
            self.has_init,
            self.has_scripts,
            self.has_examples,
            self.has_tests,
        ]
        return sum(checks) / len(checks)


class SkillHealthChecker:
    """Validates skill directory structure and health.

    Args:
        skills_root: Root skills directory.

    Example::

        checker = SkillHealthChecker()
        report = checker.check_all()
        print(
            f"Total: {report['total_skills']}, Complete: {report['health_distribution']['complete']}"
        )
    """

    def __init__(self, skills_root: Path | None = None) -> None:
        self._root = skills_root or _SKILLS_ROOT

    def check_skill(self, skill_dir: Path) -> SkillHealth:
        """Check a single skill directory.

        Args:
            skill_dir: Path to the skill.

        Returns:
            :class:`SkillHealth` with status data.
        """
        health = SkillHealth(name=skill_dir.name, path=str(skill_dir))

        health.has_skill_md = (skill_dir / "SKILL.md").exists()
        health.has_init = (skill_dir / "__init__.py").exists()
        health.has_scripts = (skill_dir / "scripts").is_dir()
        health.has_examples = (skill_dir / "examples").is_dir()
        health.has_tests = (
            bool(list(skill_dir.glob("test_*.py"))) or (skill_dir / "tests").is_dir()
        )

        all_files = [
            f
            for f in skill_dir.rglob("*")
            if f.is_file() and "__pycache__" not in str(f)
        ]
        health.file_count = len(all_files)

        return health

    def check_all(self) -> dict[str, Any]:
        """Check all skills.

        Returns:
            dict with ``total_skills``, ``health_distribution``, and ``skills`` list.
        """
        start = time.monotonic()
        skills: list[dict] = []

        for d in sorted(self._root.iterdir()):
            if not d.is_dir() or d.name.startswith(("_", ".")) or d.name == "skills":
                continue

            health = self.check_skill(d)
            skills.append(
                {
                    "name": health.name,
                    "health": health.health,
                    "completeness": round(health.completeness, 2),
                    "file_count": health.file_count,
                    "has_skill_md": health.has_skill_md,
                    "has_tests": health.has_tests,
                }
            )

        elapsed = (time.monotonic() - start) * 1000
        dist = {"complete": 0, "functional": 0, "stub": 0}
        for s in skills:
            dist[s["health"]] = dist.get(s["health"], 0) + 1

        return {
            "total_skills": len(skills),
            "health_distribution": dist,
            "scan_duration_ms": round(elapsed, 1),
            "skills": skills,
        }


__all__ = [
    "SkillHealth",
    "SkillHealthChecker",
]
