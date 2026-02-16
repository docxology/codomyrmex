"""Automated merge conflict resolution strategies.

Provides Git merge conflict detection and programmatic resolution
using AST-aware and heuristic-based strategies.
"""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ResolutionStrategy(Enum):
    """Strategy for resolving merge conflicts."""
    OURS = "ours"
    THEIRS = "theirs"
    UNION = "union"
    MANUAL = "manual"


@dataclass
class ConflictBlock:
    """A single conflict block within a file."""
    file_path: str
    start_line: int
    ours_content: str
    theirs_content: str
    ancestor_content: str = ""
    resolved: bool = False
    resolution: str = ""

    @property
    def is_trivial(self) -> bool:
        """Check if conflict is trivially resolvable (whitespace-only diff)."""
        return self.ours_content.strip() == self.theirs_content.strip()


@dataclass
class MergeConflictReport:
    """Report of all conflicts in a repository."""
    conflicts: list[ConflictBlock] = field(default_factory=list)
    files_affected: int = 0
    auto_resolved: int = 0
    manual_required: int = 0


class MergeResolver:
    """Programmatic Git merge conflict resolution.

    Detects conflicts in working tree files and provides
    strategies for automatic and semi-automatic resolution.
    """

    CONFLICT_START = re.compile(r"^<<<<<<<\s*(.*)")
    CONFLICT_MIDDLE = re.compile(r"^=======")
    CONFLICT_END = re.compile(r"^>>>>>>>\s*(.*)")

    def __init__(self, repo_path: Path) -> None:
        self._repo = repo_path

    def detect_conflicts(self) -> MergeConflictReport:
        """Scan all files in the repo for merge conflict markers."""
        report = MergeConflictReport()
        files_with_conflicts: set[str] = set()

        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            capture_output=True, text=True, cwd=self._repo,
        )
        conflict_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]

        for file_name in conflict_files:
            file_path = self._repo / file_name
            if not file_path.exists():
                continue
            blocks = self._parse_conflicts(file_path, file_name)
            if blocks:
                files_with_conflicts.add(file_name)
                report.conflicts.extend(blocks)

        report.files_affected = len(files_with_conflicts)
        return report

    def _parse_conflicts(self, path: Path, rel_name: str) -> list[ConflictBlock]:
        """Parse conflict markers from a file."""
        blocks: list[ConflictBlock] = []
        lines = path.read_text().splitlines()
        i = 0
        while i < len(lines):
            if self.CONFLICT_START.match(lines[i]):
                start = i
                ours_lines: list[str] = []
                theirs_lines: list[str] = []
                i += 1
                while i < len(lines) and not self.CONFLICT_MIDDLE.match(lines[i]):
                    ours_lines.append(lines[i])
                    i += 1
                i += 1  # skip =======
                while i < len(lines) and not self.CONFLICT_END.match(lines[i]):
                    theirs_lines.append(lines[i])
                    i += 1
                blocks.append(ConflictBlock(
                    file_path=rel_name,
                    start_line=start + 1,
                    ours_content="\n".join(ours_lines),
                    theirs_content="\n".join(theirs_lines),
                ))
            i += 1
        return blocks

    def resolve_file(self, file_path: str,
                     strategy: ResolutionStrategy = ResolutionStrategy.OURS) -> bool:
        """Resolve all conflicts in a file using a strategy."""
        full_path = self._repo / file_path
        if not full_path.exists():
            return False

        content = full_path.read_text()
        if "<<<<<<" not in content:
            return True

        resolved = self._apply_strategy(content, strategy)
        full_path.write_text(resolved)
        subprocess.run(["git", "add", file_path], cwd=self._repo)
        return True

    def _apply_strategy(self, content: str, strategy: ResolutionStrategy) -> str:
        """Apply resolution strategy to conflicted content."""
        lines = content.splitlines()
        result: list[str] = []
        i = 0
        while i < len(lines):
            if self.CONFLICT_START.match(lines[i]):
                ours: list[str] = []
                theirs: list[str] = []
                i += 1
                while i < len(lines) and not self.CONFLICT_MIDDLE.match(lines[i]):
                    ours.append(lines[i])
                    i += 1
                i += 1
                while i < len(lines) and not self.CONFLICT_END.match(lines[i]):
                    theirs.append(lines[i])
                    i += 1
                if strategy == ResolutionStrategy.OURS:
                    result.extend(ours)
                elif strategy == ResolutionStrategy.THEIRS:
                    result.extend(theirs)
                elif strategy == ResolutionStrategy.UNION:
                    result.extend(ours)
                    result.extend(theirs)
            else:
                result.append(lines[i])
            i += 1
        return "\n".join(result) + "\n"

    def auto_resolve_trivial(self) -> int:
        """Auto-resolve all trivial conflicts (whitespace-only)."""
        report = self.detect_conflicts()
        resolved = 0
        for conflict in report.conflicts:
            if conflict.is_trivial:
                self.resolve_file(conflict.file_path, ResolutionStrategy.OURS)
                resolved += 1
        return resolved
