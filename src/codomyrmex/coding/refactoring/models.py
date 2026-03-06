"""Refactoring data models: Location, Change, RefactoringResult, Refactoring ABC."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RefactoringType(Enum):
    """Types of refactoring operations."""

    RENAME = "rename"
    EXTRACT_FUNCTION = "extract_function"
    EXTRACT_CLASS = "extract_class"
    INLINE = "inline"
    MOVE = "move"
    ENCAPSULATE_FIELD = "encapsulate_field"
    PULL_UP = "pull_up"
    PUSH_DOWN = "push_down"
    REPLACE_CONDITIONAL = "replace_conditional"


@dataclass
class Location:
    """Source code location."""

    file_path: str
    line: int
    column: int = 0
    end_line: int | None = None
    end_column: int | None = None

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line}:{self.column}"


@dataclass
class Change:
    """A single code change."""

    location: Location
    old_text: str
    new_text: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.location.file_path,
            "line": self.location.line,
            "old": self.old_text,
            "new": self.new_text,
            "description": self.description,
        }


@dataclass
class RefactoringResult:
    """Result of a refactoring operation."""

    success: bool
    changes: list[Change]
    description: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def apply_to_files(self) -> None:
        """Apply all changes to files (sorted bottom-to-top per file)."""
        changes_by_file: dict[str, list[Change]] = {}
        for change in self.changes:
            changes_by_file.setdefault(change.location.file_path, []).append(change)

        for file_path, file_changes in changes_by_file.items():
            file_changes.sort(key=lambda c: c.location.line, reverse=True)

            with open(file_path) as f:
                lines = f.readlines()

            for change in file_changes:
                idx = change.location.line - 1
                if 0 <= idx < len(lines):
                    lines[idx] = lines[idx].replace(change.old_text, change.new_text)

            with open(file_path, "w") as f:
                f.writelines(lines)


class Refactoring(ABC):
    """Abstract base class for refactorings."""

    refactoring_type: RefactoringType

    @abstractmethod
    def analyze(self) -> list[str]:
        """Analyze the refactoring and return any warnings/errors."""

    @abstractmethod
    def execute(self) -> RefactoringResult:
        """Execute the refactoring."""

    @abstractmethod
    def preview(self) -> str:
        """Generate a preview of the changes."""
