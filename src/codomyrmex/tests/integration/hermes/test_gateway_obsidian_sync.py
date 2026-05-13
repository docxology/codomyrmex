"""Integration tests for Hermes session syncing to Obsidian Vaults."""

from pathlib import Path

from codomyrmex.agentic_memory.obsidian import ObsidianVault
from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.hermes.hermes_client import HermesClient


class StaticHermesClient(HermesClient):
    """Hermes client variant that returns a local response for sync testing."""

    def _execute_primary(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        return AgentResponse(
            content="Hello from the test assistant!",
            error=None,
            metadata={"backend": "test"},
            execution_time=0.1,
        )


def test_hermes_client_syncs_session_to_obsidian(tmp_path: Path) -> None:
    """Verify HermesClient natively syncs sessions to an Obsidian vault when configured.

    This is a zero-mock test using the real SQLite session store and a real temp
    directory as the Obsidian vault.
    """
    vault_path = tmp_path / "hermes_vault"
    db_path = tmp_path / "sessions.db"

    # Initialize the client with the vault path
    client = StaticHermesClient(
        config={
            "hermes_backend": "none",  # Prevent actual LLM calls
            "obsidian_vault": str(vault_path),
            "hermes_session_db": str(db_path),
        }
    )

    response = client.chat_session("Hello Hermes!", session_name="TestSyncSession")

    assert response.is_success()
    assert "Hello from the test assistant!" in response.content

    # Verify the obsidian vault received it
    vault = ObsidianVault(vault_path)
    notes = list(vault.notes.values())

    assert len(notes) == 1
    note = notes[0]

    # Check that it's in the Sessions/ directory
    assert "Sessions" in note.path.parts
    assert note.title == "TestSyncSession"

    # Check frontmatter
    assert note.frontmatter.get("type") == "hermes_session"
    assert "session_id" in note.frontmatter

    # Check content includes both user and assistant roles
    assert "### User" in note.content
    assert "Hello Hermes!" in note.content
    assert "### Assistant" in note.content
    assert "Hello from the test assistant!" in note.content
