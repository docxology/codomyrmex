"""Integration tests for Hermes Vault Search and Recall."""

from pathlib import Path

from codomyrmex.agentic_memory.obsidian import ObsidianVault
from codomyrmex.agentic_memory.obsidian.crud import create_note
from codomyrmex.agents.hermes.mcp_tools import hermes_search_vault


def test_hermes_search_vault_tool(tmp_path: Path) -> None:
    """Verify hermes_search_vault properly queries the Obsidian vault indexing."""
    vault_path = tmp_path / "search_vault"
    vault_path.mkdir(parents=True, exist_ok=True)
    vault = ObsidianVault(vault_path)

    # Create notes
    create_note(
        vault,
        "TestSession 1",
        content="User requested a graph database architecture. Hermes suggested Neo4j.",
    )
    create_note(
        vault, "TestSession 2", content="We discussed Python AST parsing tools."
    )
    create_note(
        vault,
        "Project Alpha",
        content="The core architecture depends heavily on the Neo4j backend.",
    )

    # Search for Neo4j
    result = hermes_search_vault(str(vault_path), "Neo4j", use_regex=False)

    assert result["status"] == "success", result.get("message")
    assert result["count"] == 2

    notes_found = {res["note"] for res in result["results"]}
    assert "TestSession 1" in notes_found
    assert "Project Alpha" in notes_found

    # regex search for Python
    result_regex = hermes_search_vault(str(vault_path), r"Python\sAST", use_regex=True)
    assert result_regex["status"] == "success"
    assert result_regex["count"] == 1
    assert result_regex["results"][0]["note"] == "TestSession 2"


def test_hermes_search_vault_empty_results(tmp_path: Path) -> None:
    """Verify empty search results don't raise errors."""
    vault_path = tmp_path / "search_vault_empty"
    vault_path.mkdir(parents=True, exist_ok=True)
    vault = ObsidianVault(vault_path)
    create_note(vault, "TestSession 1", content="Hello world.")

    result = hermes_search_vault(str(vault_path), "NonexistentPhrase", use_regex=False)

    assert result["status"] == "success"
    assert result["count"] == 0
    assert result["results"] == []
