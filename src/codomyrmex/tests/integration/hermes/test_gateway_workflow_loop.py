"""Integration tests for Hermes Workflow Engine Loop."""


from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.hermes.hermes_client import HermesClient


class TestHermesClient(HermesClient):
    """Test implementation of HermesClient simulating task orchestration."""

    def __init__(self, db_path: str):
        super().__init__(
            config={"hermes_session_db": db_path, "hermes_backend": "none"}
        )
        self.call_count = 0

    def execute(self, request: AgentRequest, max_tokens: int | None = None) -> AgentResponse:
        """Simulate LLM creating and resolving tasks iteratively."""
        self.call_count += 1

        # We need to simulate the side-effects of tool calls by calling the MCP tools directly
        from codomyrmex.agents.hermes.mcp_tools import (
            hermes_create_task,
            hermes_update_task_status,
        )

        session_id = None
        # Extract session_id from system prompt
        for line in request.prompt.split("\n"):
            if "Your current session ID is" in line:
                session_id = line.split("'")[1]
                break

        if not session_id:
            return AgentResponse(
                content="Error: No session ID", error=None, metadata={}
            )

        if self.call_count == 1:
            # First turn: break down plan
            hermes_create_task(session_id, "step1", "First step")
            hermes_create_task(session_id, "step2", "Second step", ["step1"])
            return AgentResponse(content="Created tasks.", error=None, metadata={})

        if self.call_count == 2:
            # Second turn: complete step 1
            hermes_update_task_status(session_id, "step1", "completed", "Done step 1")
            return AgentResponse(content="Completed step 1.", error=None, metadata={})

        if self.call_count == 3:
            # Third turn: complete step 2
            hermes_update_task_status(session_id, "step2", "completed", "Done step 2")
            return AgentResponse(content="Completed step 2.", error=None, metadata={})

        return AgentResponse(content="All done.", error=None, metadata={})


def test_hermes_autonomous_loop(tmp_path, monkeypatch):
    """Verify chat_session loops until tasks are completed."""
    db_path = str(tmp_path / "sessions.db")
    client = TestHermesClient(db_path)

    # Make sure tools running in execute modify the specific DB path
    import codomyrmex.agents.hermes.mcp_tools as tools_module

    monkeypatch.setattr(tools_module, "_get_client", lambda *args, **kwargs: client)

    response = client.chat_session(prompt="Do a two step complex task.")

    assert response.is_success()
    assert response.metadata["autonomous_turns"] == 2  # The loop iterated 2 extra times
    assert client.call_count == 3

    tasks = response.metadata["workflow_tasks"]
    assert "step1" in tasks
    assert "step2" in tasks
    assert tasks["step1"]["status"] == "completed"
    assert tasks["step2"]["status"] == "completed"
