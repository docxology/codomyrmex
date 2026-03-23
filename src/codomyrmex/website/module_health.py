"""Module health data provider.

Scans the repository to produce per-module health metrics:
file count, LOC, test count, and lint status.

Example::

    provider = ModuleHealthProvider()
    modules = provider.get_all_modules()
    for m in modules:
        print(f"{m['name']}: {m['loc']} LOC, {m['test_count']} tests")
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC_ROOT = _REPO_ROOT / "src" / "codomyrmex"
_TEST_ROOT = _SRC_ROOT / "tests"


@dataclass(frozen=True)
class ModuleHealth:
    """Health summary for a single module.

    Attributes:
        name: Module directory name.
        file_count: Number of ``.py`` source files.
        loc: Total lines of code.
        test_count: Number of ``test_*.py`` files matching this module.
        has_readme: Whether ``README.md`` exists.
        has_spec: Whether ``SPEC.md`` exists.
        has_agents: Whether ``AGENTS.md`` exists.
    """

    name: str
    file_count: int
    loc: int
    test_count: int
    has_readme: bool
    has_spec: bool
    has_agents: bool

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "file_count": self.file_count,
            "loc": self.loc,
            "test_count": self.test_count,
            "has_readme": self.has_readme,
            "has_spec": self.has_spec,
            "has_agents": self.has_agents,
            "doc_completeness": sum([self.has_readme, self.has_spec, self.has_agents])
            / 3.0,
        }


class ModuleHealthProvider:
    """Scans the source tree to produce module health metrics.

    Args:
        src_root: Root of module directories. Defaults to ``src/codomyrmex/``.
        test_root: Root of test directories. Defaults to ``src/codomyrmex/tests/``.

    Example::

        provider = ModuleHealthProvider()
        health = provider.get_module("auth")
        print(health.loc, health.test_count)
    """

    def __init__(
        self,
        src_root: Path | None = None,
        test_root: Path | None = None,
    ) -> None:
        self._src_root = src_root or _SRC_ROOT
        self._test_root = test_root or _TEST_ROOT
        self._cache: dict[str, ModuleHealth] | None = None
        self._cache_time: float = 0.0

    def _discover_modules(self) -> list[str]:
        """Find all top-level module directories."""
        return sorted(
            d.name
            for d in self._src_root.iterdir()
            if d.is_dir()
            and (d / "__init__.py").exists()
            and not d.name.startswith("_")
            and d.name != "tests"
        )

    def _count_tests(self, module_name: str) -> int:
        """Count test files related to a module."""
        count = 0
        for test_dir in (self._test_root / "unit", self._test_root / "integration"):
            if not test_dir.exists():
                continue
            # Check module-specific test directory
            mod_test_dir = test_dir / module_name
            if mod_test_dir.is_dir():
                count += sum(
                    1
                    for f in mod_test_dir.rglob("test_*.py")
                    if "__pycache__" not in str(f)
                )
            # Check top-level test files matching module name
            for f in test_dir.glob(f"test_{module_name}*.py"):
                count += 1
        return count

    def _scan_module(self, name: str) -> ModuleHealth:
        """Scan a single module directory."""
        mod_dir = self._src_root / name
        py_files = [f for f in mod_dir.rglob("*.py") if "__pycache__" not in str(f)]
        loc = sum(
            len(f.read_text(encoding="utf-8", errors="replace").splitlines())
            for f in py_files
        )

        return ModuleHealth(
            name=name,
            file_count=len(py_files),
            loc=loc,
            test_count=self._count_tests(name),
            has_readme=(mod_dir / "README.md").exists(),
            has_spec=(mod_dir / "SPEC.md").exists(),
            has_agents=(mod_dir / "AGENTS.md").exists(),
        )

    def get_all_modules(self, force_refresh: bool = False) -> list[ModuleHealth]:
        """Get health data for all modules.

        Results are cached for 60 seconds unless *force_refresh* is True.

        Args:
            force_refresh: Force a fresh scan.

        Returns:
            list of :class:`ModuleHealth` for every module.
        """
        if (
            not force_refresh
            and self._cache is not None
            and (time.time() - self._cache_time) < 60
        ):
            return list(self._cache.values())

        modules = self._discover_modules()
        cache: dict[str, ModuleHealth] = {}
        for name in modules:
            try:
                cache[name] = self._scan_module(name)
            except Exception:
                logger.warning("Failed to scan module %s", name, exc_info=True)

        self._cache = cache
        self._cache_time = time.time()
        logger.info("Scanned %d modules", len(cache))
        return list(cache.values())

    def get_module(self, name: str) -> ModuleHealth | None:
        """Get health data for a specific module.

        Args:
            name: Module name.

        Returns:
            :class:`ModuleHealth` or ``None`` if not found.
        """
        modules = self.get_all_modules()
        for m in modules:
            if m.name == name:
                return m
        return None

    def get_summary(self) -> dict[str, Any]:
        """Get aggregate summary statistics.

        Returns:
            dict with total modules, files, LOC, tests, and doc completeness.
        """
        modules = self.get_all_modules()
        return {
            "total_modules": len(modules),
            "total_files": sum(m.file_count for m in modules),
            "total_loc": sum(m.loc for m in modules),
            "total_tests": sum(m.test_count for m in modules),
            "avg_doc_completeness": (
                sum(
                    sum([m.has_readme, m.has_spec, m.has_agents]) / 3.0 for m in modules
                )
                / len(modules)
                if modules
                else 0.0
            ),
            "modules_with_tests": sum(1 for m in modules if m.test_count > 0),
        }

    def to_json(self) -> str:
        """Serialize all module health data to JSON.

        Returns:
            JSON string with module list and summary.
        """
        modules = self.get_all_modules()
        return json.dumps(
            {
                "modules": [m.to_dict() for m in modules],
                "summary": self.get_summary(),
                "timestamp": time.time(),
            },
            indent=2,
        )


__all__ = [
    "ModuleHealth",
    "ModuleHealthProvider",
]
