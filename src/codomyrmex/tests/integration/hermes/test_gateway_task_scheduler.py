"""Integration tests for Hermes internal task scheduling MCP tools."""

import pytest

from codomyrmex.agents.hermes.hermes_client import HermesClient
from codomyrmex.agents.hermes.mcp_tools import (
    hermes_create_task,
    hermes_update_task_status,
)
from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore


@pytest.fixture
def test_client(tmp_path):
    """Fixture providing a HermesClient with a temporary session DB."""
    db_path = tmp_path / "sessions.db"
    return HermesClient(
        config={"hermes_session_db": str(db_path), "hermes_backend": "none"}
    )


def test_hermes_create_and_update_task(test_client, monkeypatch) -> None:
    """Verify hermes_create_task and hermes_update_task_status mutate session metadata."""

    # Patch _get_client to return our test_client with isolated DB
    import codomyrmex.agents.hermes.mcp_tools as tools_module

    monkeypatch.setattr(
        tools_module, "_get_client", lambda *args, **kwargs: test_client
    )

    # 1. Setup session
    with SQLiteSessionStore(test_client._session_db_path) as store:
        session = HermesSession()
        store.save(session)
        session_id = session.session_id

    # 2. Create task
    res_create = hermes_create_task(
        session_id=session_id,
        name="task_1",
        description="Write the test fixture",
        depends_on=[],
    )
    assert res_create["status"] == "success", res_create.get("message")
    assert res_create["task"]["status"] == "pending"

    # 3. Verify task exists in DB
    with SQLiteSessionStore(test_client._session_db_path) as store:
        session = store.load(session_id)
        assert "task_1" in session.metadata["workflow_tasks"]
        assert session.metadata["workflow_tasks"]["task_1"]["status"] == "pending"

    # 4. Update task status
    res_update = hermes_update_task_status(
        session_id=session_id,
        name="task_1",
        status="completed",
        result="Fixture written successfully.",
    )
    assert res_update["status"] == "success"
    assert res_update["task"]["status"] == "completed"

    # 5. Verify update in DB
    with SQLiteSessionStore(test_client._session_db_path) as store:
        session = store.load(session_id)
        assert session.metadata["workflow_tasks"]["task_1"]["status"] == "completed"
        assert (
            session.metadata["workflow_tasks"]["task_1"]["result"]
            == "Fixture written successfully."
        )


def test_hermes_create_task_invalid_session(test_client, monkeypatch) -> None:
    """Verify tool behavior when provided an invalid session ID."""
    import codomyrmex.agents.hermes.mcp_tools as tools_module

    monkeypatch.setattr(
        tools_module, "_get_client", lambda *args, **kwargs: test_client
    )

    res = hermes_create_task("invalid-123", "task_2", "Description")
    assert res["status"] == "error"
    assert "not found" in res["message"]
