"""Data models for the rules submodule.

Provides Rule, RuleSection, RuleSet, and RulePriority — the core types
used by the loader, registry, and engine to represent .cursorrules files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class RulePriority(Enum):
    """Hierarchy level of a coding rule.

    Lower value = higher specificity = wins over higher-value rules.
    """

    FILE_SPECIFIC = 1  # Highest priority — wins over all others
    MODULE = 2
    CROSS_MODULE = 3
    GENERAL = 4  # Lowest priority — always present, never overrides


@dataclass
class RuleSection:
    """One numbered section from a .cursorrules file (§0–§7)."""

    number: int
    title: str   # e.g. "Coding Standards & Practices for Python"
    content: str

    def to_dict(self) -> dict[str, Any]:
        return {"number": self.number, "title": self.title, "content": self.content}


@dataclass
class Rule:
    """Parsed representation of a single .cursorrules file."""

    name: str               # e.g. "python", "agentic_memory", "general"
    priority: RulePriority
    file_path: Path
    sections: list[RuleSection]
    raw_content: str

    def get_section(self, number: int) -> RuleSection | None:
        """Return the section with the given number, or None if absent."""
        for s in self.sections:
            if s.number == number:
                return s
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "priority": self.priority.name,
            "file_path": str(self.file_path),
            "sections": [s.to_dict() for s in self.sections],
            "raw_content": self.raw_content,
        }


@dataclass
class RuleSet:
    """A collection of rules applicable to a given context."""

    rules: list[Rule] = field(default_factory=list)

    def resolved(self) -> list[Rule]:
        """Return rules sorted highest-priority first (FILE_SPECIFIC=1 → GENERAL=4)."""
        return sorted(self.rules, key=lambda r: r.priority.value)

    def to_dict(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.resolved()]
