"""InlineRefactoring: replace a symbol reference with its definition value."""

import re

from .models import Change, Location, Refactoring, RefactoringResult, RefactoringType


class InlineRefactoring(Refactoring):
    """Inline a variable or simple function by substituting its value at call sites."""

    refactoring_type = RefactoringType.INLINE

    def __init__(self, file_path: str, symbol_name: str):
        self.file_path = file_path
        self.symbol_name = symbol_name

    def _find_definition(self, content: str) -> tuple[int, str] | None:
        """Return (line_number, rhs_value) for the assignment, or None."""
        pattern = re.compile(
            rf"^(\s*){re.escape(self.symbol_name)}\s*=\s*(.+)$", re.MULTILINE
        )
        match = pattern.search(content)
        if not match:
            return None
        line_num = content[: match.start()].count("\n") + 1
        return line_num, match.group(2).strip()

    def analyze(self) -> list[str]:
        """Warn if the symbol has many usages (inlining may bloat code)."""
        with open(self.file_path) as f:
            content = f.read()
        count = len(re.findall(r"\b" + re.escape(self.symbol_name) + r"\b", content))
        warnings = []
        if count > 5:
            warnings.append(f"Symbol has {count} usages, inlining may increase code size")
        return warnings

    def execute(self) -> RefactoringResult:
        """Replace all usages of symbol_name with its defined value."""
        warnings = self.analyze()
        try:
            with open(self.file_path) as f:
                content = f.read()

            defn = self._find_definition(content)
            if defn is None:
                return RefactoringResult(
                    success=False, changes=[],
                    description=f"Could not find definition of '{self.symbol_name}'",
                    errors=["Definition not found"],
                )

            def_line, value = defn
            usage_pattern = re.compile(r"\b" + re.escape(self.symbol_name) + r"\b")
            changes = [
                Change(
                    location=Location(self.file_path, line_num, m.start()),
                    old_text=self.symbol_name,
                    new_text=value,
                    description=f"Inline '{self.symbol_name}'",
                )
                for line_num, line in enumerate(content.split("\n"), 1)
                if line_num != def_line
                for m in usage_pattern.finditer(line)
            ]

            return RefactoringResult(
                success=True, changes=changes,
                description=f"Inlined '{self.symbol_name}' with value '{value}'",
                warnings=warnings,
            )
        except Exception as e:
            return RefactoringResult(success=False, changes=[], description=str(e), errors=[str(e)])

    def preview(self) -> str:
        result = self.execute()
        return f"Inline: {self.symbol_name}\nChanges: {len(result.changes)}\n{result.description}"
