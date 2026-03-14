"""Integration tests for Hermes Context Summarization."""

import pytest

from codomyrmex.agents.hermes.hermes_client import HermesClient


def test_hermes_context_summarization_integration(tmp_path, monkeypatch):
    """Verify that a long session correctly triggers the _summarize_context pipeline."""
    # We will use the Zero-Mock strategy by utilizing the local test backend or overriding
    # the execute implementation to simply echo back deterministic responses.

    client = HermesClient()
    client.config = {}
    # Configure an aggressively small window
    client.config["max_session_messages"] = 4

    # Override db path to be isolated
    db_path = tmp_path / "test_hermes_sessions.db"
    client._session_db_path = str(db_path)

    # We patch the execute method locally for this client instance to avoid actual LLM calls
    # but still execute the real logic in chat_session and _summarize_context.

    from codomyrmex.agents.core import AgentResponse

    def mock_execute(request):
        prompt = request.prompt
        if "Format your output strictly as a dense timeline or list" in prompt:
            return AgentResponse(
                content="SUMMARY_GENERATED: The user is testing.",
                error=None,
                metadata={},
            )
        if "Extract any permanent user preferences" in prompt:
            return AgentResponse(
                content="FACT: User likes short tests.", error=None, metadata={}
            )

        return AgentResponse(content=f"ACK: {prompt[-20:]}", error=None, metadata={})

    monkeypatch.setattr(client, "execute", mock_execute)

    # Turn 1
    resp1 = client.chat_session("Hello Hermes, I am testing the system.")
    session_id = resp1.metadata.get("session_id")
    assert session_id is not None

    # Turn 2
    resp2 = client.chat_session("Here is some more context.", session_id=session_id)
    # Turn 3 - this should add messages, making it hit the threshold > 4
    # Messages structure:
    # After Turn 1: user, assistant (2 msgs)
    # After Turn 2: user, assistant (4 msgs)
    # On start of Turn 3, user is added -> 5 msgs. len(session.messages) > 4
    # _summarize_context should trigger.

    resp3 = client.chat_session("Trigger the limit now.", session_id=session_id)

    # Reload session to check state
    from codomyrmex.agents.hermes.session import SQLiteSessionStore

    with SQLiteSessionStore(str(db_path)) as store:
        session = store.load(session_id)
        assert session is not None

        messages = session.messages
        # Original: User1, Asst1, User2, Asst2, User3 (5 total) -> summarizer takes oldest 2.
        # Leaves User2, Asst2, User3
        # Injects summary -> Total becomes 1 summary + 3 existing + 1 Asst3 = 5
        # Wait, half of 5 is 2. The remaining is 3. New summary = 1. Add asst response = 1. Total = 5.

        assert len(messages) <= 6
        assert messages[0]["role"] == "system"
        assert "<SESSION_SUMMARY>" in messages[0]["content"]
        assert "SUMMARY_GENERATED" in messages[0]["content"]

        facts = session.metadata.get("extracted_facts", "")
        assert "FACT: User likes short tests." in facts
