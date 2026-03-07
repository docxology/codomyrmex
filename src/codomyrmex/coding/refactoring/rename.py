"""RenameRefactoring: whole-word rename across a file."""

import re

from .models import Change, Location, Refactoring, RefactoringResult, RefactoringType


class RenameRefactoring(Refactoring):
    """Rename a symbol (variable, function, class, etc.) by whole-word substitution."""

    refactoring_type = RefactoringType.RENAME

    def __init__(
        self, file_path: str, old_name: str, new_name: str, scope: str = "file"
    ):
        self.file_path = file_path
        self.old_name = old_name
        self.new_name = new_name
        self.scope = scope

    def _is_valid_identifier(self, name: str) -> bool:
        return name.isidentifier() and not name.startswith("_")

    def _find_occurrences(self, content: str) -> list[tuple[int, int, int]]:
        """Return (line_num, start_col, end_col) for each whole-word occurrence."""
        pattern = re.compile(r"\b" + re.escape(self.old_name) + r"\b")
        return [
            (line_num, m.start(), m.end())
            for line_num, line in enumerate(content.split("\n"), 1)
            for m in pattern.finditer(line)
        ]

    def analyze(self) -> list[str]:
        """Warn if new_name is invalid, shadows a builtin, or already exists."""
        warnings = []
        if not self._is_valid_identifier(self.new_name):
            warnings.append(f"'{self.new_name}' may not be a valid identifier")
        if self.new_name in dir(__builtins__):
            warnings.append(f"'{self.new_name}' shadows a built-in name")

        with open(self.file_path) as f:
            content = f.read()

        if re.search(r"\b" + re.escape(self.new_name) + r"\b", content):
            warnings.append(f"'{self.new_name}' already exists in the file")

        return warnings

    def execute(self) -> RefactoringResult:
        """Build Change list for every occurrence of old_name in the file."""
        warnings = self.analyze()
        try:
            with open(self.file_path) as f:
                content = f.read()

            changes = [
                Change(
                    location=Location(self.file_path, line_num, start, line_num, end),
                    old_text=self.old_name,
                    new_text=self.new_name,
                    description=f"Rename '{self.old_name}' to '{self.new_name}'",
                )
                for line_num, start, end in self._find_occurrences(content)
            ]

            return RefactoringResult(
                success=True,
                changes=changes,
                description=f"Renamed '{self.old_name}' to '{self.new_name}' ({len(changes)} occurrences)",
                warnings=warnings,
            )
        except Exception as e:
            return RefactoringResult(
                success=False, changes=[], description=str(e), errors=[str(e)]
            )

    def preview(self) -> str:
        """Preview the rename changes (first 10 shown)."""
        result = self.execute()
        lines = [
            f"Rename: {self.old_name} -> {self.new_name}",
            f"File: {self.file_path}",
            f"Changes: {len(result.changes)}",
        ]
        for change in result.changes[:10]:
            lines.append(
                f"  Line {change.location.line}: {change.old_text} -> {change.new_text}"
            )
        if len(result.changes) > 10:
            lines.append(f"  ... and {len(result.changes) - 10} more")
        return "\n".join(lines)
