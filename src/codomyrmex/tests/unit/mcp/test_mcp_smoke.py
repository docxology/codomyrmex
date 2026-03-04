"""Smoke tests — ensure every mcp_tools module imports and exposes tools."""

import pytest


@pytest.mark.unit
class TestMCPToolsImport:
    """Verify that all mcp_tools modules import without errors."""

    def test_git_operations_mcp_tools_import(self):
        from codomyrmex.git_operations import mcp_tools

        assert hasattr(mcp_tools, "git_check_availability")
        assert hasattr(mcp_tools, "git_repo_status")
        assert hasattr(mcp_tools, "git_current_branch")
        assert hasattr(mcp_tools, "git_diff")
        assert hasattr(mcp_tools, "git_log")
        assert hasattr(mcp_tools, "git_init")
        assert hasattr(mcp_tools, "git_clone")
        assert hasattr(mcp_tools, "git_commit")
        assert hasattr(mcp_tools, "git_create_branch")
        assert hasattr(mcp_tools, "git_switch_branch")
        assert hasattr(mcp_tools, "git_pull")
        assert hasattr(mcp_tools, "git_push")

    def test_containerization_mcp_tools_import(self):
        from codomyrmex.containerization import mcp_tools

        assert hasattr(mcp_tools, "container_runtime_status")
        assert hasattr(mcp_tools, "container_build")
        assert hasattr(mcp_tools, "container_list")
        assert hasattr(mcp_tools, "container_security_scan")

    def test_coding_mcp_tools_import(self):
        from codomyrmex.coding import mcp_tools

        assert hasattr(mcp_tools, "code_execute")
        assert hasattr(mcp_tools, "code_list_languages")
        assert hasattr(mcp_tools, "code_review_file")
        assert hasattr(mcp_tools, "code_review_project")
        assert hasattr(mcp_tools, "code_debug")

    def test_search_mcp_tools_import(self):
        from codomyrmex.search import mcp_tools

        assert hasattr(mcp_tools, "search_documents")
        assert hasattr(mcp_tools, "search_index_query")
        assert hasattr(mcp_tools, "search_fuzzy")

    def test_formal_verification_mcp_tools_import(self):
        from codomyrmex.formal_verification import mcp_tools

        assert hasattr(mcp_tools, "clear_model")
        assert hasattr(mcp_tools, "add_item")
        assert hasattr(mcp_tools, "solve_model")


@pytest.mark.unit
class TestMCPToolsExecution:
    """Verify that safe MCP tools execute correctly."""

    def test_git_check_availability(self):
        from codomyrmex.git_operations.mcp_tools import git_check_availability

        result = git_check_availability()
        assert result["status"] == "ok"
        assert isinstance(result["git_available"], bool)

    def test_code_list_languages(self):
        from codomyrmex.coding.mcp_tools import code_list_languages

        result = code_list_languages()
        assert result["status"] == "ok"
        assert "python" in result["languages"]

    def test_container_runtime_status(self):
        from codomyrmex.containerization.mcp_tools import container_runtime_status

        result = container_runtime_status()
        assert result["status"] == "ok"
        assert isinstance(result["runtimes"], dict)

    def test_git_is_repo(self, tmp_path):
        from codomyrmex.git_operations.mcp_tools import git_is_repo

        result = git_is_repo(str(tmp_path))
        assert result["status"] == "ok"
        assert result["is_git_repository"] is False

    def test_search_documents(self):
        from codomyrmex.search.mcp_tools import search_documents

        docs = [
            "The quick brown fox",
            "jumped over the lazy dog",
        ]
        result = search_documents("fox", docs)
        assert result["status"] == "ok"
        assert len(result["results"]) > 0


@pytest.mark.unit
class TestMCPToolMetadata:
    """Verify that @mcp_tool decorator attaches metadata."""

    def test_git_tool_has_metadata(self):
        from codomyrmex.git_operations.mcp_tools import git_check_availability

        meta = getattr(git_check_availability, "_mcp_tool_meta", None)
        assert meta is not None
        assert meta["category"] == "git_operations"
        assert "description" in meta

    def test_coding_tool_has_metadata(self):
        from codomyrmex.coding.mcp_tools import code_execute

        meta = getattr(code_execute, "_mcp_tool_meta", None)
        assert meta is not None
        assert meta["category"] == "coding"

    def test_search_tool_has_metadata(self):
        from codomyrmex.search.mcp_tools import search_documents

        meta = getattr(search_documents, "_mcp_tool_meta", None)
        assert meta is not None
        assert meta["category"] == "search"
