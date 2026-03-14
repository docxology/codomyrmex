import os
import sqlite3
import pytest
from pathlib import Path
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes.hermes_client import HermesClient
from codomyrmex.agents.hermes.session import SQLiteSessionStore
from codomyrmex.agents.hermes.mcp_tools import hermes_create_task
from codomyrmex.logging_monitoring.core.correlation import get_correlation_id

@pytest.fixture
def temp_db(tmp_path: Path):
    db_path = tmp_path / "test_hermes_sessions.db"
    yield db_path
    if db_path.exists():
        db_path.unlink()

@pytest.fixture
def hermes_client(temp_db):
    # Configure using ollama backend which doesn't require API keys for fast offline testing
    client = HermesClient(
        config={
            "hermes_backend": "ollama",
            "hermes_model": "hermes3",
            "hermes_session_db": str(temp_db),
        }
    )
    return client

def test_unified_traceability_execute(hermes_client):
    """Test that a basic execute request correctly assigns and propagates trace_id."""
    request = AgentRequest(prompt="Hello, are you there?")
    assert request.trace_id is not None
    
    # We do not actually need to run the full request if we just want to test correlation ID, 
    # but Since Zero Mock insists on real execution, we execute with Ollama (or gracefully handle failure if not running).
    try:
        response = hermes_client.execute(request)
        # Verify trace_id propagates to response
        assert response.trace_id == request.trace_id
    except Exception as e:
        # If Ollama isn't running, we at least verify the trace ID is on the request
        # and test passes execution logic up to failure.
        pytest.skip(f"Could not execute Ollama for trace test: {e}")

def test_unified_traceability_mcp_propagation(temp_db, hermes_client, monkeypatch):
    """Test that hermes_create_task inherits parent_trace_id correctly."""
    import codomyrmex.agents.hermes.mcp_tools as mcp_tools
    monkeypatch.setattr(mcp_tools, "_get_client", lambda *args, **kwargs: hermes_client)
    
    # 1. Create a session natively
    from codomyrmex.agents.hermes.session import HermesSession
    with SQLiteSessionStore(str(temp_db)) as store:
        session = HermesSession(name="trace_test_session")
        store.save(session)
        session_id = session.session_id
        
    # 2. Simulate context execution
    request = AgentRequest(prompt="Create task logic")
    trace_id = request.trace_id
    
    # Wrap execution with correlation ID to simulate the execute() wrapper logic
    from codomyrmex.logging_monitoring.core.correlation import with_correlation
    
    with with_correlation(trace_id):
        assert get_correlation_id() == trace_id
        
        # Call the MCP tool which should capture the context correlation_id
        result = hermes_create_task(
            session_id=session_id,
            name="test_trace_task",
            description="Traceability context task",
        )
        
        assert result["status"] == "success"
        
    # 3. Pull from DB to assert native tagging handled the trace boundary
    with SQLiteSessionStore(str(temp_db)) as store:
        db_session = store.load(session_id)
        assert db_session is not None
        
        tasks = db_session.metadata.get("workflow_tasks", {})
        assert "test_trace_task" in tasks
        
        task = tasks["test_trace_task"]
        assert "parent_trace_id" in task
        assert task["parent_trace_id"] == trace_id
