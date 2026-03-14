from pathlib import Path

import pytest

from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore


def test_sqlite_fts5_sync_and_search(tmp_path: Path):
    """Test that the FTS5 table is automatically synced and searchable."""
    db_path = tmp_path / "test_hermes_sessions.db"

    with SQLiteSessionStore(db_path) as store:
        # Create a session with identifiable text
        session1 = HermesSession(name="Code Review Task")
        session1.add_message("user", "Please check the proxy server implementation.")
        session1.add_message(
            "assistant",
            "I will analyze the reverse proxy logic and authentication headers.",
        )
        store.save(session1)

        # Create another session
        session2 = HermesSession(name="Documentation Updates")
        session2.add_message("user", "Update the README.")
        store.save(session2)

        # Test basic search
        results = store.search_fts("proxy")
        assert len(results) == 1
        assert results[0]["session_id"] == session1.session_id
        # Check snippet generation (snippet bolting depends on FTS5 defaults, but should contain the word)
        assert "proxy" in results[0]["messages_snippet"].lower()

        # Test updating a session (should update FTS via au trigger)
        session2.add_message("assistant", "The README proxy section has been updated.")
        store.save(session2)

        results2 = store.search_fts("proxy")
        assert len(results2) == 2

        # Test deletion (should update FTS via ad trigger)
        store.delete(session1.session_id)
        results3 = store.search_fts("proxy")
        assert len(results3) == 1
        assert results3[0]["session_id"] == session2.session_id


def test_sqlite_fts_migration(tmp_path: Path):
    """Test that existing databases are migrated correctly to include the FTS index."""
    import sqlite3

    db_path = tmp_path / "test_migration.db"

    # Create an old schema without FTS
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE hermes_sessions (
            session_id TEXT PRIMARY KEY,
            name TEXT,
            parent_session_id TEXT,
            messages TEXT NOT NULL,
            metadata TEXT NOT NULL DEFAULT '{}',
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
    """)
    # Insert a record natively
    import json
    import time

    conn.execute(
        "INSERT INTO hermes_sessions VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "legacy-123",
            "Legacy Task",
            None,
            json.dumps([{"role": "user", "content": "Find the secret legacy key."}]),
            "{}",
            time.time(),
            time.time(),
        ),
    )
    conn.commit()
    conn.close()

    # Now instantiate the store, which should run migrations
    with SQLiteSessionStore(db_path) as store:
        results = store.search_fts("legacy")
        assert len(results) == 1
        assert results[0]["session_id"] == "legacy-123"
