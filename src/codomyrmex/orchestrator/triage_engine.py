"""Module triage engine for Tier-3 module classification.

Scans modules and classifies them into promote/archive/merge/stub
based on LOC, test coverage, and activity signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class TriageDecision(Enum):
    """Triage disposition for a module."""
    PROMOTE = "promote"
    ARCHIVE = "archive"
    MERGE = "merge"
    STUB = "stub"
    ACTIVE = "active"  # Already healthy, no action needed


@dataclass
class ModuleProfile:
    """Profile of a single module.

    Attributes:
        name: Module name.
        path: Module path.
        loc: Lines of Python code.
        file_count: Number of ``.py`` files.
        has_tests: Whether tests exist.
        has_init: Whether ``__init__.py`` exists.
        has_mcp_tools: Whether ``mcp_tools.py`` exists.
        has_spec: Whether ``SPEC.md`` exists.
        decision: Triage disposition.
        merge_target: If merging, target package.
    """

    name: str
    path: str = ""
    loc: int = 0
    file_count: int = 0
    has_tests: bool = False
    has_init: bool = False
    has_mcp_tools: bool = False
    has_spec: bool = False
    decision: TriageDecision = TriageDecision.STUB
    merge_target: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "name": self.name,
            "loc": self.loc,
            "files": self.file_count,
            "decision": self.decision.value,
            "has_tests": self.has_tests,
            "has_mcp_tools": self.has_mcp_tools,
        }


@dataclass
class TriageReport:
    """Complete triage report.

    Attributes:
        modules: All profiled modules.
        promote: Modules to promote.
        archive: Modules to archive.
        merge: Modules to merge.
        stub: Modules to keep as stubs.
        active: Modules already healthy.
    """

    modules: list[ModuleProfile] = field(default_factory=list)

    @property
    def promote(self) -> list[ModuleProfile]:
        """Execute Promote operations natively."""
        return [m for m in self.modules if m.decision == TriageDecision.PROMOTE]

    @property
    def archive(self) -> list[ModuleProfile]:
        """Execute Archive operations natively."""
        return [m for m in self.modules if m.decision == TriageDecision.ARCHIVE]

    @property
    def merge(self) -> list[ModuleProfile]:
        """Execute Merge operations natively."""
        return [m for m in self.modules if m.decision == TriageDecision.MERGE]

    @property
    def stub(self) -> list[ModuleProfile]:
        """Execute Stub operations natively."""
        return [m for m in self.modules if m.decision == TriageDecision.STUB]

    @property
    def active(self) -> list[ModuleProfile]:
        """Execute Active operations natively."""
        return [m for m in self.modules if m.decision == TriageDecision.ACTIVE]

    def summary(self) -> dict[str, Any]:
        """Execute Summary operations natively."""
        return {
            "total": len(self.modules),
            "promote": len(self.promote),
            "archive": len(self.archive),
            "merge": len(self.merge),
            "stub": len(self.stub),
            "active": len(self.active),
        }


# Merge rules: module_name → target package
MERGE_MAP: dict[str, str] = {
    "cache": "performance/caching",
    "compression": "utils/compression",
    "feature_flags": "config_management/flags",
}

# Archive list: modules too small or speculative
ARCHIVE_SET: frozenset[str] = frozenset({
    "embodiment", "evolutionary_ai", "module_template", "dark", "quantum",
})

# Promote list: modules worth investing in
PROMOTE_SET: frozenset[str] = frozenset({
    "wallet", "networking", "telemetry", "skills", "auth",
})


class TriageEngine:
    """Classify modules into triage buckets.

    Usage::

        engine = TriageEngine()
        profile = engine.profile_module("my_module", Path("/path/to/module"))
        report = engine.triage_all(Path("/path/to/src"))
    """

    def __init__(
        self,
        min_active_loc: int = 2000,
        archive_threshold: int = 100,
    ) -> None:
        """Execute   Init   operations natively."""
        self._min_active_loc = min_active_loc
        self._archive_threshold = archive_threshold

    def profile_module(self, name: str, module_path: Path) -> ModuleProfile:
        """Profile a single module directory."""
        profile = ModuleProfile(name=name, path=str(module_path))

        if not module_path.exists():
            return profile

        py_files = list(module_path.rglob("*.py"))
        profile.file_count = len(py_files)
        profile.has_init = (module_path / "__init__.py").exists()
        profile.has_mcp_tools = (module_path / "mcp_tools.py").exists()
        profile.has_spec = (module_path / "SPEC.md").exists()

        total_loc = 0
        for py_file in py_files:
            try:
                lines = py_file.read_text().splitlines()
                total_loc += sum(1 for ln in lines if ln.strip() and not ln.strip().startswith("#"))
            except (OSError, UnicodeDecodeError):
                pass
        profile.loc = total_loc

        # Check for tests
        profile.has_tests = any("test" in f.name.lower() for f in py_files)

        # Classify
        profile.decision = self._classify(profile)

        return profile

    def triage_all(self, src_path: Path) -> TriageReport:
        """Triage all modules under a source directory.

        Args:
            src_path: Path to the source root.

        Returns:
            ``TriageReport`` with all module profiles.
        """
        report = TriageReport()

        if not src_path.exists():
            return report

        for item in sorted(src_path.iterdir()):
            if item.is_dir() and not item.name.startswith(("_", ".")):
                profile = self.profile_module(item.name, item)
                report.modules.append(profile)

        logger.info("Triage complete", extra=report.summary())
        return report

    def _classify(self, profile: ModuleProfile) -> TriageDecision:
        """Classify a module based on its profile."""
        name = profile.name

        # Explicit classifications
        if name in MERGE_MAP:
            profile.merge_target = MERGE_MAP[name]
            return TriageDecision.MERGE

        if name in ARCHIVE_SET:
            return TriageDecision.ARCHIVE

        if name in PROMOTE_SET:
            return TriageDecision.PROMOTE

        # Heuristic: large modules with tests are active
        if profile.loc >= self._min_active_loc and profile.has_tests:
            return TriageDecision.ACTIVE

        # Heuristic: decent size with MCP tools
        if profile.loc >= 500 and profile.has_mcp_tools:
            return TriageDecision.ACTIVE

        # Very small modules
        if profile.loc < self._archive_threshold and profile.file_count <= 2:
            return TriageDecision.ARCHIVE

        return TriageDecision.STUB


__all__ = [
    "ARCHIVE_SET",
    "MERGE_MAP",
    "ModuleProfile",
    "PROMOTE_SET",
    "TriageDecision",
    "TriageEngine",
    "TriageReport",
]
