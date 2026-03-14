import os
import subprocess
import pytest
from pathlib import Path
from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.hermes.hermes_client import HermesClient
from codomyrmex.agents.hermes.session import SQLiteSessionStore

@pytest.fixture
def temp_db(tmp_path: Path):
    db_path = tmp_path / "test_hermes_healing_sessions.db"
    yield db_path
    if db_path.exists():
        db_path.unlink()

@pytest.fixture
def hermes_client(temp_db):
    client = HermesClient(
        config={
            "hermes_backend": "ollama",
            "hermes_model": "hermes3",
            "hermes_session_db": str(temp_db),
        }
    )
    return client

class MockFailingClient(HermesClient):
    """A client that fakes a subprocess failure due to a missing package on its first run,
    then succeeds on the second run (simulating a successful heal sequence)."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_count = 0
        self.heal_called = False
        
    def execute(self, request: AgentRequest) -> AgentResponse:
        self.call_count += 1
        if self.call_count == 1:
            # Simulate a Python script that failed to find requests
            error_trace = "Traceback (most recent call last):\nModuleNotFoundError: No module named 'dummy_missing_pkg'"
            return AgentResponse(
                content="",
                error=error_trace,
                metadata={
                    "exit_code": 1,
                    "stderr": error_trace
                }
            )
        else:
            return AgentResponse(
                content="I have completed the task successfully.",
                error=None,
                metadata={"exit_code": 0}
            )
            
    def _heal_environment(self, package_name: str) -> dict:
        # Mock the actual uv call so we don't mess up the host environment during tests
        self.heal_called = True
        assert package_name == "dummy_missing_pkg"
        return {"success": True, "output": f"Mock healed {package_name}"}

def test_automated_healing_flow(temp_db):
    """Test that chat_session intercepts ModuleNotFoundError and triggers healing."""
    
    # We use our MockFailingClient which bypasses actual OLLAMA calls but retains
    # the exact `chat_session` workflow logic from the base class.
    client = MockFailingClient(
        config={
            "hermes_backend": "ollama",
            "hermes_session_db": str(temp_db),
        }
    )
    
    response = client.chat_session(prompt="Write a script using dummy_missing_pkg")
    
    assert client.call_count == 2
    assert client.heal_called is True
    
    # Verify metadata tracking
    with SQLiteSessionStore(str(temp_db)) as store:
        session_id = response.metadata["session_id"]
        session = store.load(session_id)
        
        assert session.metadata.get("heal_attempts") == 1
        assert session.metadata.get("heal_success_rate") == 1
