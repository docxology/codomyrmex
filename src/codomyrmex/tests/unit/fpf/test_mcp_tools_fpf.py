"""Tests for fpf MCP tools.

Zero-mock tests validating the FPF MCP tool wrappers.
"""

from __future__ import annotations

# Sample FPF-like markdown for testing
SAMPLE_FPF_MARKDOWN = """# FPF Specification v1.0.0

## Table of Contents

## A.1 - Test Pattern Alpha

### Problem
This is the problem statement.

### Solution
This is the solution.

*Keywords:* testing, alpha, patterns

## A.2 - Test Pattern Beta

### Problem
Another problem.

### Solution
Another solution.
"""


class TestFpfListTypes:
    """Tests for fpf_list_types tool."""

    def test_returns_success_status(self):
        from codomyrmex.fpf.mcp_tools import fpf_list_types

        result = fpf_list_types()
        assert result["status"] == "success"

    def test_contains_pattern_statuses(self):
        from codomyrmex.fpf.mcp_tools import fpf_list_types

        result = fpf_list_types()
        assert "pattern_statuses" in result
        assert "Stable" in result["pattern_statuses"]
        assert "Draft" in result["pattern_statuses"]

    def test_contains_concept_types(self):
        from codomyrmex.fpf.mcp_tools import fpf_list_types

        result = fpf_list_types()
        assert "concept_types" in result
        assert len(result["concept_types"]) > 0

    def test_contains_relationship_types(self):
        from codomyrmex.fpf.mcp_tools import fpf_list_types

        result = fpf_list_types()
        assert "relationship_types" in result
        assert "builds_on" in result["relationship_types"]


class TestFpfParseSpec:
    """Tests for fpf_parse_spec tool."""

    def test_parse_sample_markdown(self):
        from codomyrmex.fpf.mcp_tools import fpf_parse_spec

        result = fpf_parse_spec(markdown_content=SAMPLE_FPF_MARKDOWN)
        assert result["status"] == "success"
        assert result["pattern_count"] == 2

    def test_parse_extracts_pattern_ids(self):
        from codomyrmex.fpf.mcp_tools import fpf_parse_spec

        result = fpf_parse_spec(markdown_content=SAMPLE_FPF_MARKDOWN)
        ids = [p["id"] for p in result["patterns"]]
        assert "A.1" in ids
        assert "A.2" in ids

    def test_parse_extracts_titles(self):
        from codomyrmex.fpf.mcp_tools import fpf_parse_spec

        result = fpf_parse_spec(markdown_content=SAMPLE_FPF_MARKDOWN)
        titles = [p["title"] for p in result["patterns"]]
        assert "Test Pattern Alpha" in titles

    def test_parse_empty_markdown(self):
        from codomyrmex.fpf.mcp_tools import fpf_parse_spec

        result = fpf_parse_spec(markdown_content="# Empty spec")
        assert result["status"] == "success"
        assert result["pattern_count"] == 0

    def test_parse_with_source_path(self):
        from codomyrmex.fpf.mcp_tools import fpf_parse_spec

        result = fpf_parse_spec(
            markdown_content=SAMPLE_FPF_MARKDOWN,
            source_path="/tmp/test.md",
        )
        assert result["status"] == "success"


class TestFpfSearchPatterns:
    """Tests for fpf_search_patterns tool."""

    def test_search_finds_matching_pattern(self):
        from codomyrmex.fpf.mcp_tools import fpf_search_patterns

        result = fpf_search_patterns(
            markdown_content=SAMPLE_FPF_MARKDOWN,
            query="Alpha",
        )
        assert result["status"] == "success"
        assert result["match_count"] >= 1
        ids = [m["id"] for m in result["matches"]]
        assert "A.1" in ids

    def test_search_no_results(self):
        from codomyrmex.fpf.mcp_tools import fpf_search_patterns

        result = fpf_search_patterns(
            markdown_content=SAMPLE_FPF_MARKDOWN,
            query="xyznonexistentquery123",
        )
        assert result["status"] == "success"
        assert result["match_count"] == 0

    def test_search_returns_query_echo(self):
        from codomyrmex.fpf.mcp_tools import fpf_search_patterns

        result = fpf_search_patterns(
            markdown_content=SAMPLE_FPF_MARKDOWN,
            query="testing",
        )
        assert result["query"] == "testing"
