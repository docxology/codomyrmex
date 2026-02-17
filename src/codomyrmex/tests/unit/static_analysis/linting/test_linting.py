"""
Tests for Static Analysis Linting Module
"""

import tempfile

import pytest

from codomyrmex.coding.static_analysis.linting import (
    LineLengthRule,
    Linter,
    LintIssue,
    LintResult,
    LintSeverity,
    TodoCommentRule,
    TrailingWhitespaceRule,
    UnusedImportRule,
)


class TestLintResult:
    """Tests for LintResult."""

    def test_add_issue(self):
        """Should track issue counts."""
        result = LintResult(file_path="test.py")

        result.add_issue(LintIssue("E1", "", LintSeverity.ERROR, None, ""))
        result.add_issue(LintIssue("W1", "", LintSeverity.WARNING, None, ""))
        result.add_issue(LintIssue("I1", "", LintSeverity.INFO, None, ""))

        assert result.error_count == 1
        assert result.warning_count == 1
        assert result.has_errors


class TestLineLengthRule:
    """Tests for LineLengthRule."""

    def test_detect_long(self):
        """Should detect long lines."""
        rule = LineLengthRule(max_length=10)
        code = "x = 12345678901234567890"

        issues = rule.check(code, "test.py")

        assert len(issues) == 1

    def test_pass_short(self):
        """Should pass short lines."""
        rule = LineLengthRule(max_length=50)
        code = "x = 1"

        issues = rule.check(code, "test.py")

        assert len(issues) == 0


class TestTrailingWhitespaceRule:
    """Tests for TrailingWhitespaceRule."""

    def test_detect_trailing(self):
        """Should detect trailing whitespace."""
        rule = TrailingWhitespaceRule()
        code = "x = 1  \ny = 2"

        issues = rule.check(code, "test.py")

        assert len(issues) == 1
        assert issues[0].line_number == 1


class TestUnusedImportRule:
    """Tests for UnusedImportRule."""

    def test_detect_unused(self):
        """Should detect unused imports."""
        rule = UnusedImportRule()
        code = """
import os
import sys

print(sys.version)
"""

        issues = rule.check(code, "test.py")

        # os is unused
        assert any("os" in i.message for i in issues)


class TestTodoCommentRule:
    """Tests for TodoCommentRule."""

    def test_detect_todo(self):
        """Should detect TODO comments."""
        rule = TodoCommentRule()
        code = """
# TODO: fix this
x = 1
# FIXME: also this
"""

        issues = rule.check(code, "test.py")

        assert len(issues) == 2


class TestLinter:
    """Tests for Linter."""

    def test_lint(self):
        """Should lint content."""
        linter = Linter()
        code = "x = 1  "  # trailing whitespace

        result = linter.lint(code)

        assert result.total_issues >= 1

    def test_lint_file(self):
        """Should lint file."""
        code = "def foo(): pass  \n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            linter = Linter()
            result = linter.lint_file(f.name)

        assert result.total_issues >= 1

    def test_add_rule(self):
        """Should add custom rule."""
        linter = Linter()
        linter.add_rule(LineLengthRule(max_length=5))

        result = linter.lint("x = 123456")

        # Should find line length issue
        assert any(i.rule_id == "E501" for i in result.issues)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
