"""Multi-turn Hermes session with persistence.

Creates a ``HermesSession``, executes multiple turns through
``HermesClient``, persists via ``SQLiteSessionStore``, then reloads
and verifies conversation continuity.

Usage::

    python -m codomyrmex.agents.hermes.scripts.run_session
"""

from __future__ import annotations

import json
import sys
from typing import Any

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes.hermes_client import HermesClient, HermesError
from codomyrmex.agents.hermes.session import (
    HermesSession,
    SQLiteSessionStore,
)


def run_session(
    prompts: list[str] | None = None,
    *,
    db_path: str = ":memory:",
    backend: str = "auto",
    model: str = "hermes3",
) -> dict[str, Any]:
    """Run a multi-turn session with SQLite persistence.

    Args:
        prompts: List of prompts to send in sequence. Defaults to a
            demo pair.
        db_path: SQLite database path. Use ``":memory:"`` for ephemeral.
        backend: Backend preference.
        model: Ollama model name.

    Returns:
        Dict with session summary: ``session_id``, ``message_count``,
        ``messages``, ``persisted``, ``reloaded``.
    """
    if prompts is None:
        prompts = [
            "What is active inference in one sentence?",
            "Now explain it for a 5-year-old.",
        ]

    client = HermesClient(
        config={
            "hermes_backend": backend,
            "hermes_model": model,
        }
    )

    session = HermesSession(metadata={"backend": client.active_backend})
    store = SQLiteSessionStore(db_path=db_path)

    try:
        for prompt_text in prompts:
            session.add_message("user", prompt_text)

            try:
                request = AgentRequest(prompt=prompt_text)
                response = client.execute(request)
                content = (
                    response.content
                    if response.is_success()
                    else f"[error] {response.error}"
                )
            except HermesError as exc:
                content = f"[error] {exc}"

            session.add_message("assistant", content)

        # Persist
        store.save(session)

        # Reload and verify
        reloaded = store.load(session.session_id)
        reload_ok = (
            reloaded is not None
            and reloaded.session_id == session.session_id
            and reloaded.message_count == session.message_count
        )

        # List sessions to confirm
        all_ids = store.list_sessions()

        return {
            "status": "success",
            "session_id": session.session_id,
            "message_count": session.message_count,
            "messages": session.messages,
            "persisted": session.session_id in all_ids,
            "reloaded": reload_ok,
            "backend": client.active_backend,
        }
    finally:
        store.close()


def main() -> None:
    """CLI entry point."""
    result = run_session(db_path="/tmp/hermes_sessions.db")
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
