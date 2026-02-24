"""
Code refactoring utilities.

Provides automated refactoring patterns and transformations.
"""

import ast
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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
        """Execute   Str   operations natively."""
        return f"{self.file_path}:{self.line}:{self.column}"


@dataclass
class Change:
    """A single code change."""
    location: Location
    old_text: str
    new_text: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
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
        """Apply all changes to files."""
        changes_by_file: dict[str, list[Change]] = {}
        for change in self.changes:
            file_path = change.location.file_path
            if file_path not in changes_by_file:
                changes_by_file[file_path] = []
            changes_by_file[file_path].append(change)

        for file_path, file_changes in changes_by_file.items():
            # Sort changes by line in reverse order to apply from bottom to top
            file_changes.sort(key=lambda c: c.location.line, reverse=True)

            with open(file_path) as f:
                lines = f.readlines()

            for change in file_changes:
                line_idx = change.location.line - 1
                if 0 <= line_idx < len(lines):
                    lines[line_idx] = lines[line_idx].replace(
                        change.old_text,
                        change.new_text
                    )

            with open(file_path, 'w') as f:
                f.writelines(lines)


class Refactoring(ABC):
    """Abstract base class for refactorings."""

    refactoring_type: RefactoringType

    @abstractmethod
    def analyze(self) -> list[str]:
        """Analyze the refactoring and return any warnings/errors."""
        pass

    @abstractmethod
    def execute(self) -> RefactoringResult:
        """Execute the refactoring."""
        pass

    @abstractmethod
    def preview(self) -> str:
        """Generate a preview of the changes."""
        pass


class RenameRefactoring(Refactoring):
    """Rename a symbol (variable, function, class, etc.)."""

    refactoring_type = RefactoringType.RENAME

    def __init__(
        self,
        file_path: str,
        old_name: str,
        new_name: str,
        scope: str = "file",  # file, module, project
    ):
        """Execute   Init   operations natively."""
        self.file_path = file_path
        self.old_name = old_name
        self.new_name = new_name
        self.scope = scope
        self._locations: list[Location] = []

    def _is_valid_identifier(self, name: str) -> bool:
        """Check if name is a valid Python identifier."""
        return name.isidentifier() and not name.startswith('_')

    def _find_occurrences(self, content: str) -> list[tuple[int, int, int]]:
        """Find all occurrences of the old name."""
        occurrences = []
        lines = content.split('\n')

        # Pattern to match whole word only
        pattern = re.compile(r'\b' + re.escape(self.old_name) + r'\b')

        for line_num, line in enumerate(lines, 1):
            for match in pattern.finditer(line):
                occurrences.append((line_num, match.start(), match.end()))

        return occurrences

    def analyze(self) -> list[str]:
        """Execute Analyze operations natively."""
        warnings = []

        if not self._is_valid_identifier(self.new_name):
            warnings.append(f"'{self.new_name}' may not be a valid identifier")

        if self.new_name in dir(__builtins__):
            warnings.append(f"'{self.new_name}' shadows a built-in name")

        # Check for existing name
        with open(self.file_path) as f:
            content = f.read()

        if re.search(r'\b' + re.escape(self.new_name) + r'\b', content):
            warnings.append(f"'{self.new_name}' already exists in the file")

        return warnings

    def execute(self) -> RefactoringResult:
        """Execute Execute operations natively."""
        warnings = self.analyze()

        try:
            with open(self.file_path) as f:
                content = f.read()

            occurrences = self._find_occurrences(content)

            changes = []
            for line_num, start, end in occurrences:
                changes.append(Change(
                    location=Location(self.file_path, line_num, start, line_num, end),
                    old_text=self.old_name,
                    new_text=self.new_name,
                    description=f"Rename '{self.old_name}' to '{self.new_name}'",
                ))

            return RefactoringResult(
                success=True,
                changes=changes,
                description=f"Renamed '{self.old_name}' to '{self.new_name}' ({len(changes)} occurrences)",
                warnings=warnings,
            )

        except Exception as e:
            return RefactoringResult(
                success=False,
                changes=[],
                description=str(e),
                errors=[str(e)],
            )

    def preview(self) -> str:
        """Execute Preview operations natively."""
        result = self.execute()
        lines = [f"Rename: {self.old_name} -> {self.new_name}"]
        lines.append(f"File: {self.file_path}")
        lines.append(f"Changes: {len(result.changes)}")

        for change in result.changes[:10]:
            lines.append(f"  Line {change.location.line}: {change.old_text} -> {change.new_text}")

        if len(result.changes) > 10:
            lines.append(f"  ... and {len(result.changes) - 10} more")

        return "\n".join(lines)


class ExtractFunctionRefactoring(Refactoring):
    """Extract selected code into a new function."""

    refactoring_type = RefactoringType.EXTRACT_FUNCTION

    def __init__(
        self,
        file_path: str,
        start_line: int,
        end_line: int,
        function_name: str,
        parameters: list[str] | None = None,
    ):
        """Execute   Init   operations natively."""
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.function_name = function_name
        self.parameters = parameters or []

    def _detect_variables(self, code: str) -> tuple[list[str], list[str]]:
        """Detect variables used and defined in the code."""
        # Simple regex-based detection for demonstration
        # In production, use AST analysis

        # Find assignments (defined)
        defined = set(re.findall(r'^\s*(\w+)\s*=', code, re.MULTILINE))

        # Find all identifiers (used)
        used = set(re.findall(r'\b([a-zA-Z_]\w*)\b', code))

        # Filter out Python keywords and builtins
        import keyword
        used = used - set(keyword.kwlist) - set(dir(__builtins__))

        # External variables = used but not defined
        external = used - defined

        return list(external), list(defined)

    def analyze(self) -> list[str]:
        """Execute Analyze operations natively."""
        warnings = []

        if not self.function_name.isidentifier():
            warnings.append(f"'{self.function_name}' is not a valid function name")

        with open(self.file_path) as f:
            lines = f.readlines()

        if self.start_line < 1 or self.end_line > len(lines):
            warnings.append("Line range is out of bounds")

        return warnings

    def execute(self) -> RefactoringResult:
        """Execute Execute operations natively."""
        warnings = self.analyze()

        try:
            with open(self.file_path) as f:
                lines = f.readlines()

            # Extract the code
            extracted_lines = lines[self.start_line - 1:self.end_line]
            extracted_code = ''.join(extracted_lines)

            # Detect variables
            params, returns = self._detect_variables(extracted_code)

            # If parameters not provided, use detected ones
            if not self.parameters:
                self.parameters = params

            # Determine indentation
            first_line = extracted_lines[0]
            original_indent = len(first_line) - len(first_line.lstrip())

            # Build new function
            func_lines = [f"def {self.function_name}({', '.join(self.parameters)}):\n"]
            for line in extracted_lines:
                # Adjust indentation
                stripped = line[original_indent:] if len(line) > original_indent else line
                func_lines.append(f"    {stripped}")

            if returns:
                func_lines.append(f"    return {', '.join(returns)}\n")

            new_function = ''.join(func_lines)

            # Build function call
            if returns:
                call = f"{' ' * original_indent}{', '.join(returns)} = {self.function_name}({', '.join(self.parameters)})\n"
            else:
                call = f"{' ' * original_indent}{self.function_name}({', '.join(self.parameters)})\n"

            changes = [
                Change(
                    location=Location(self.file_path, self.start_line),
                    old_text=extracted_code,
                    new_text=call,
                    description="Replace code with function call",
                ),
            ]

            return RefactoringResult(
                success=True,
                changes=changes,
                description=f"Extracted function '{self.function_name}'",
                warnings=warnings,
            )

        except Exception as e:
            return RefactoringResult(
                success=False,
                changes=[],
                description=str(e),
                errors=[str(e)],
            )

    def preview(self) -> str:
        """Execute Preview operations natively."""
        result = self.execute()
        return f"Extract Function: {self.function_name}\n" + \
               f"Lines: {self.start_line}-{self.end_line}\n" + \
               f"Parameters: {', '.join(self.parameters)}"


class InlineRefactoring(Refactoring):
    """Inline a function or variable."""

    refactoring_type = RefactoringType.INLINE

    def __init__(
        self,
        file_path: str,
        symbol_name: str,
    ):
        """Execute   Init   operations natively."""
        self.file_path = file_path
        self.symbol_name = symbol_name

    def analyze(self) -> list[str]:
        """Execute Analyze operations natively."""
        warnings = []

        with open(self.file_path) as f:
            content = f.read()

        # Count usages
        pattern = re.compile(r'\b' + re.escape(self.symbol_name) + r'\b')
        count = len(pattern.findall(content))

        if count > 5:
            warnings.append(f"Symbol has {count} usages, inlining may increase code size")

        return warnings

    def execute(self) -> RefactoringResult:
        """Execute Execute operations natively."""
        warnings = self.analyze()

        try:
            with open(self.file_path) as f:
                content = f.read()

            # Find the definition (simple variable assignment)
            definition_pattern = re.compile(
                rf'^(\s*){re.escape(self.symbol_name)}\s*=\s*(.+)$',
                re.MULTILINE
            )
            match = definition_pattern.search(content)

            if not match:
                return RefactoringResult(
                    success=False,
                    changes=[],
                    description=f"Could not find definition of '{self.symbol_name}'",
                    errors=["Definition not found"],
                )

            value = match.group(2).strip()

            # Find all usages (excluding the definition)
            usage_pattern = re.compile(r'\b' + re.escape(self.symbol_name) + r'\b')

            changes = []
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                if line_num == content[:match.start()].count('\n') + 1:
                    continue  # Skip the definition line

                for m in usage_pattern.finditer(line):
                    changes.append(Change(
                        location=Location(self.file_path, line_num, m.start()),
                        old_text=self.symbol_name,
                        new_text=value,
                        description=f"Inline '{self.symbol_name}'",
                    ))

            return RefactoringResult(
                success=True,
                changes=changes,
                description=f"Inlined '{self.symbol_name}' with value '{value}'",
                warnings=warnings,
            )

        except Exception as e:
            return RefactoringResult(
                success=False,
                changes=[],
                description=str(e),
                errors=[str(e)],
            )

    def preview(self) -> str:
        """Execute Preview operations natively."""
        result = self.execute()
        return f"Inline: {self.symbol_name}\n" + \
               f"Changes: {len(result.changes)}\n" + \
               result.description


def create_refactoring(
    refactoring_type: RefactoringType,
    **kwargs
) -> Refactoring:
    """Factory function to create refactoring instances."""
    refactorings = {
        RefactoringType.RENAME: RenameRefactoring,
        RefactoringType.EXTRACT_FUNCTION: ExtractFunctionRefactoring,
        RefactoringType.INLINE: InlineRefactoring,
    }

    refactoring_class = refactorings.get(refactoring_type)
    if not refactoring_class:
        raise ValueError(f"Unsupported refactoring type: {refactoring_type}")

    return refactoring_class(**kwargs)


__all__ = [
    "RefactoringType",
    "Location",
    "Change",
    "RefactoringResult",
    "Refactoring",
    "RenameRefactoring",
    "ExtractFunctionRefactoring",
    "InlineRefactoring",
    "create_refactoring",
]
