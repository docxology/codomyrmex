"""Integration tests for Hermes Error-Correction Handoffs."""


from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.hermes.hermes_client import HermesClient


class TestFailedHermesClient(HermesClient):
    """Test implementation of HermesClient simulating a recovered subprocess failure."""

    def __init__(self, db_path: str):
        super().__init__(
            config={"hermes_session_db": db_path, "hermes_backend": "none"}
        )
        self.call_count = 0
        self.intercepted_prompts = []

    def execute(self, request: AgentRequest, max_tokens: int | None = None) -> AgentResponse:
        """Simulate LLM creating a tool call that fails, then recovering."""
        self.call_count += 1
        self.intercepted_prompts.append(request.prompt)

        if self.call_count == 1:
            # First turn: LLM attempts something, but we simulate a subprocess failure
            return AgentResponse(
                content="<tool_call>execute_script.py</tool_call>",
                error='Traceback (most recent call last):\n  File "script.py", line 2\n    sys.exit(1)\nSystemExit: 1',
                metadata={
                    "exit_code": 1,
                    "stderr": 'Traceback (most recent call last):\n  File "script.py", line 2\n    sys.exit(1)\nSystemExit: 1',
                },
            )

        if self.call_count == 2:
            # Second turn: LLM should have received the <FAILED_TRACE> in the prompt
            assert "<FAILED_TRACE>" in request.prompt
            assert "SystemExit: 1" in request.prompt
            return AgentResponse(
                content="Ah, I see the error. I fixed the script.",
                error=None,
                metadata={"exit_code": 0},
            )

        return AgentResponse(content="Done.", error=None, metadata={"exit_code": 0})


def test_recursive_retry_on_subprocess_failure(tmp_path):
    """Verify chat_session intercepts failed executions and dynamically prompts recovery."""
    db_path = str(tmp_path / "sessions.db")
    client = TestFailedHermesClient(db_path)

    response = client.chat_session(prompt="Run the data extraction script.")

    # It should have succeeded on the second turn
    assert response.is_success()
    assert response.metadata.get("autonomous_turns", 0) == 1
    assert client.call_count == 2

    # Verify the second prompt contained the recovery instructions
    assert "<FAILED_TRACE>" in client.intercepted_prompts[1]
