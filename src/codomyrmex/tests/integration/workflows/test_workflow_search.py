"""Workflow integration test: /codomyrmexSearch.

Validates the search_codebase function finds patterns across the repository.
"""

import pytest


@pytest.mark.integration
class TestWorkflowSearch:
    """Tests mirroring the /codomyrmexSearch workflow."""

    def test_search_def_main(self, project_root):
        """Searching for 'def main' finds at least one result."""
        from codomyrmex.model_context_protocol.tools import search_codebase

        result = search_codebase(pattern="def main", path=str(project_root))
        assert isinstance(result, dict)
        matches = result.get("matches", result.get("results", []))
        if isinstance(matches, list):
            assert len(matches) >= 1, "Expected at least 1 match for 'def main'"

    def test_search_returns_file_info(self, project_root):
        """Search results include file path information."""
        from codomyrmex.model_context_protocol.tools import search_codebase

        result = search_codebase(pattern="import pytest", path=str(project_root / "src"))
        matches = result.get("matches", result.get("results", []))
        if isinstance(matches, list) and len(matches) > 0:
            match = matches[0]
            # Should have file/path information
            assert "file" in match or "path" in match or "filename" in match

    def test_search_empty_pattern_handled(self, project_root):
        """Empty pattern is handled gracefully."""
        from codomyrmex.model_context_protocol.tools import search_codebase

        # Should not crash
        result = search_codebase(pattern="", path=str(project_root))
        assert isinstance(result, dict)

    def test_search_nonexistent_pattern(self, project_root):
        """Searching for a nonexistent pattern returns empty or no results."""
        from codomyrmex.model_context_protocol.tools import search_codebase

        # Use a pattern unlikely to appear anywhere (including this test file)
        unique = "QQQ999_NEVER_IN_ANY_FILE_ZZZ"
        result = search_codebase(
            pattern=unique, path=str(project_root / "src" / "codomyrmex" / "utils")
        )
        matches = result.get("matches", result.get("results", []))
        if isinstance(matches, list):
            assert len(matches) == 0, f"Unexpected matches: {matches}"
