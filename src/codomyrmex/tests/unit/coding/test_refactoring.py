"""Zero-mock tests for coding.refactoring module.

Verifies RenameRefactoring and related functionality using real files.
No mocks.
"""

import pytest
from codomyrmex.coding.refactoring.rename import RenameRefactoring
from codomyrmex.coding.refactoring.models import RefactoringResult

@pytest.fixture
def sample_file(tmp_path):
    p = tmp_path / "script.py"
    p.write_text("def foo():\n    x = 1\n    return x + foo()\n")
    return str(p)

@pytest.mark.unit
class TestRenameRefactoring:
    """Tests for RenameRefactoring."""

    def test_rename_variable(self, sample_file):
        refactor = RenameRefactoring(sample_file, "x", "y")
        result = refactor.execute()

        assert isinstance(result, RefactoringResult)
        assert result.success is True
        assert len(result.changes) == 2
        assert result.changes[0].new_text == "y"
        assert "Renamed 'x' to 'y'" in result.description

    def test_rename_function(self, sample_file):
        refactor = RenameRefactoring(sample_file, "foo", "bar")
        result = refactor.execute()

        assert result.success is True
        assert len(result.changes) == 2
        assert all(c.new_text == "bar" for c in result.changes)

    def test_analyze_warnings(self, sample_file):
        # Rename to something that already exists
        refactor = RenameRefactoring(sample_file, "x", "foo")
        warnings = refactor.analyze()
        assert any("already exists" in w for w in warnings)

    def test_preview(self, sample_file):
        refactor = RenameRefactoring(sample_file, "x", "y")
        preview = refactor.preview()
        assert "Rename: x -> y" in preview
        assert "Changes: 2" in preview

    def test_invalid_identifier_warning(self, sample_file):
        refactor = RenameRefactoring(sample_file, "x", "123_invalid")
        warnings = refactor.analyze()
        assert any("not be a valid identifier" in w for w in warnings)
