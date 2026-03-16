"""ExtractFunctionRefactoring: lift a code range into a new function."""

import re

from .models import Change, Location, Refactoring, RefactoringResult, RefactoringType


class ExtractFunctionRefactoring(Refactoring):
    """Extract selected lines into a new function."""

    refactoring_type = RefactoringType.EXTRACT_FUNCTION

    def __init__(
        self,
        file_path: str,
        start_line: int,
        end_line: int,
        function_name: str,
        parameters: list[str] | None = None,
    ):
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.function_name = function_name
        self.parameters = parameters or []

    def _detect_variables(self, code: str) -> tuple[list[str], list[str]]:
        """Return (external_vars, defined_vars) using simple regex heuristics."""
        import keyword

        defined = set(re.findall(r"^\s*(\w+)\s*=", code, re.MULTILINE))
        used = set(re.findall(r"\b([a-zA-Z_]\w*)\b", code))
        used -= set(keyword.kwlist) | set(dir(__builtins__))
        return list(used - defined), list(defined)

    def _build_function_def(
        self, extracted_lines: list[str], returns: list[str]
    ) -> str:
        """Build the new function definition string."""
        first = extracted_lines[0]
        indent = len(first) - len(first.lstrip())
        params_str = ", ".join(self.parameters)
        body = "".join(
            f"    {line[indent:]}" if len(line) > indent else f"    {line}"
            for line in extracted_lines
        )
        suffix = f"    return {', '.join(returns)}\n" if returns else ""
        return f"def {self.function_name}({params_str}):\n{body}{suffix}"

    def analyze(self) -> list[str]:
        """Validate the refactoring parameters and return any warnings.

        Checks that the function name is a valid Python identifier and that
        the specified line range falls within the file's bounds.

        Returns:
            List of warning messages. Empty if all checks pass.

        Example:
            >>> refactoring = ExtractFunctionRefactoring(
            ...     "example.py", 10, 20, "extracted_func"
            ... )
            >>> warnings = refactoring.analyze()
            >>> if not warnings:
            ...     print("All checks passed")
        """
        warnings = []
        if not self.function_name.isidentifier():
            warnings.append(f"'{self.function_name}' is not a valid function name")
        with open(self.file_path) as f:
            lines = f.readlines()
        if self.start_line < 1 or self.end_line > len(lines):
            warnings.append("Line range is out of bounds")
        return warnings

    def execute(self) -> RefactoringResult:
        """Extract code range into a new function, replacing it with a call."""
        warnings = self.analyze()
        try:
            with open(self.file_path) as f:
                lines = f.readlines()

            extracted = lines[self.start_line - 1 : self.end_line]
            code = "".join(extracted)
            params, returns = self._detect_variables(code)
            if not self.parameters:
                self.parameters = params

            first = extracted[0]
            orig_indent = " " * (len(first) - len(first.lstrip()))
            params_str = ", ".join(self.parameters)
            if returns:
                call = f"{orig_indent}{', '.join(returns)} = {self.function_name}({params_str})\n"
            else:
                call = f"{orig_indent}{self.function_name}({params_str})\n"

            changes = [
                Change(
                    location=Location(self.file_path, self.start_line),
                    old_text=code,
                    new_text=call,
                    description="Replace code with function call",
                )
            ]

            return RefactoringResult(
                success=True,
                changes=changes,
                description=f"Extracted function '{self.function_name}'",
                warnings=warnings,
            )
        except Exception as e:
            return RefactoringResult(
                success=False, changes=[], description=str(e), errors=[str(e)]
            )

    def preview(self) -> str:
        """Generate a preview of the extraction operation.

        Executes the refactoring analysis and returns a human-readable
        summary of what would be extracted.

        Returns:
            A formatted string describing the extraction operation,
            including the target function name, line range, and parameters.

        Example:
            >>> refactoring = ExtractFunctionRefactoring(
            ...     "example.py", 10, 20, "extracted_func", ["x", "y"]
            ... )
            >>> print(refactoring.preview())
            Extract Function: extracted_func
            Lines: 10-20
            Parameters: x, y
        """
        self.execute()
        return (
            f"Extract Function: {self.function_name}\n"
            f"Lines: {self.start_line}-{self.end_line}\n"
            f"Parameters: {', '.join(self.parameters)}"
        )
