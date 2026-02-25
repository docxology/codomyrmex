"""Tests for MCP tool category taxonomy.

Validates that the auto-classification system correctly assigns
every tool to one of {analysis, generation, execution, query, mutation}.
"""

import pytest

from codomyrmex.model_context_protocol.quality.taxonomy import (
    TaxonomyReport,
    ToolCategory,
    categorize_all_tools,
    categorize_tool,
    generate_taxonomy_report,
)


class TestToolCategory:
    """Enum and basic classification tests."""

    def test_category_values(self):
        """All 5 categories exist."""
        assert len(ToolCategory) == 5
        expected = {"analysis", "generation", "execution", "query", "mutation"}
        assert {c.value for c in ToolCategory} == expected

    @pytest.mark.parametrize("tool,expected", [
        ("codomyrmex.analyze_file", ToolCategory.ANALYSIS),
        ("codomyrmex.analyze_project", ToolCategory.ANALYSIS),
        ("codomyrmex.code_review_file", ToolCategory.ANALYSIS),
        ("codomyrmex.checksum_file", ToolCategory.ANALYSIS),
        ("codomyrmex.obsidian_vault_stats", ToolCategory.ANALYSIS),
    ])
    def test_analysis_tools(self, tool, expected):
        """Test functionality: analysis tools."""
        assert categorize_tool(tool) == expected

    @pytest.mark.parametrize("tool,expected", [
        ("codomyrmex.create_bar_chart", ToolCategory.GENERATION),
        ("codomyrmex.create_line_plot", ToolCategory.GENERATION),
        ("codomyrmex.create_git_branch_diagram", ToolCategory.GENERATION),
        ("codomyrmex.generate_documentation", ToolCategory.GENERATION),
        ("codomyrmex.create_ascii_art", ToolCategory.GENERATION),
    ])
    def test_generation_tools(self, tool, expected):
        """Test functionality: generation tools."""
        assert categorize_tool(tool) == expected

    @pytest.mark.parametrize("tool,expected", [
        ("codomyrmex.execute_code", ToolCategory.EXECUTION),
        ("codomyrmex.code_execute", ToolCategory.EXECUTION),
        ("codomyrmex.run_command", ToolCategory.EXECUTION),
        ("codomyrmex.run_tests", ToolCategory.EXECUTION),
        ("codomyrmex.call_module_function", ToolCategory.EXECUTION),
    ])
    def test_execution_tools(self, tool, expected):
        """Test functionality: execution tools."""
        assert categorize_tool(tool) == expected

    @pytest.mark.parametrize("tool,expected", [
        ("codomyrmex.list_modules", ToolCategory.QUERY),
        ("codomyrmex.get_status", ToolCategory.QUERY),
        ("codomyrmex.search_codebase", ToolCategory.QUERY),
        ("codomyrmex.read_file", ToolCategory.QUERY),
        ("codomyrmex.pai_status", ToolCategory.QUERY),
        ("codomyrmex.git_diff", ToolCategory.QUERY),
        ("codomyrmex.obsidian_read_note", ToolCategory.QUERY),
    ])
    def test_query_tools(self, tool, expected):
        """Test functionality: query tools."""
        assert categorize_tool(tool) == expected

    @pytest.mark.parametrize("tool,expected", [
        ("codomyrmex.git_commit", ToolCategory.MUTATION),
        ("codomyrmex.git_push", ToolCategory.MUTATION),
        ("codomyrmex.write_file", ToolCategory.MUTATION),
        ("codomyrmex.obsidian_create_note", ToolCategory.MUTATION),
        ("codomyrmex.obsidian_delete_note", ToolCategory.MUTATION),
        ("codomyrmex.invalidate_cache", ToolCategory.MUTATION),
    ])
    def test_mutation_tools(self, tool, expected):
        """Test functionality: mutation tools."""
        assert categorize_tool(tool) == expected


class TestCategorizeAll:
    """Bulk classification tests."""

    def test_categorize_all_returns_dict(self):
        """Test functionality: categorize all returns dict."""
        names = ["codomyrmex.git_push", "codomyrmex.read_file"]
        result = categorize_all_tools(names)
        assert isinstance(result, dict)
        assert len(result) == 2
        assert result["codomyrmex.git_push"] == ToolCategory.MUTATION
        assert result["codomyrmex.read_file"] == ToolCategory.QUERY

    def test_unknown_tool_defaults_to_query(self):
        """Unrecognized tools default to query (conservative assumption)."""
        cat = categorize_tool("codomyrmex.some_unknown_tool")
        assert cat == ToolCategory.QUERY

    def test_empty_list(self):
        """Test functionality: empty list."""
        result = categorize_all_tools([])
        assert result == {}


class TestTaxonomyReport:
    """Report generation tests."""

    def test_report_structure(self):
        """Test functionality: report structure."""
        names = [
            "codomyrmex.analyze_file",
            "codomyrmex.git_push",
            "codomyrmex.create_bar_chart",
            "codomyrmex.run_command",
            "codomyrmex.list_modules",
        ]
        report = generate_taxonomy_report(names)

        assert isinstance(report, TaxonomyReport)
        assert report.total == 5
        assert report.by_category["analysis"] == 1
        assert report.by_category["mutation"] == 1
        assert report.by_category["generation"] == 1
        assert report.by_category["execution"] == 1
        assert report.by_category["query"] == 1

    def test_report_summary(self):
        """Test functionality: report summary."""
        report = generate_taxonomy_report(["codomyrmex.read_file"])
        summary = report.summary()
        assert summary["total"] == 1
        assert summary["coverage"] == "1/1"

    def test_full_tool_set_coverage(self):
        """All 63 production tools should be classifiable."""
        try:
            from codomyrmex.agents.pai.mcp_bridge import create_codomyrmex_mcp_server

            server = create_codomyrmex_mcp_server()
            tools = server._tool_registry.list_tools()
            report = generate_taxonomy_report(tools)

            assert report.total >= 60, f"Expected ≥60 tools, got {report.total}"
            assert len(report.by_category) == 5, "All 5 categories should be present"
            assert sum(report.by_category.values()) == report.total, "100% coverage"
        except ImportError:
            pytest.skip("MCP bridge not available")
