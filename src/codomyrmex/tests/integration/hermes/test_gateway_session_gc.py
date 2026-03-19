import gzip
import json
import time
from pathlib import Path

from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore


def test_sqlite_gc_prune_old_sessions(tmp_path: Path):
    """Test that old sessions are properly archived to JSON.gz and deleted from SQLite."""
    db_path = tmp_path / "test_hermes_gc.db"

    with SQLiteSessionStore(db_path) as store:
        # Create an old session
        old_session = HermesSession(name="Very Old Session")
        old_session.add_message("user", "What is the capital of France?")
        # Manually alter the updated_at to be 40 days old
        old_session.updated_at = time.time() - (40 * 86400)
        store.save(old_session)

        # Create a fresh session
        new_session = HermesSession(name="Fresh Session")
        new_session.add_message("user", "What is GraphQL?")
        store.save(new_session)

        # Verify both exist natively
        assert len(store.list_sessions()) == 2

        # Trigger GC (days_old=30)
        archived_count = store.prune_old_sessions(days_old=30)

        # Verify 1 deletion
        assert archived_count == 1
        assert len(store.list_sessions()) == 1
        assert store.load(new_session.session_id) is not None
        assert store.load(old_session.session_id) is None

        # Verify the archived file was created properly
        archive_dir = tmp_path / "sessions_archive"
        assert archive_dir.exists()

        archive_file = archive_dir / f"{old_session.session_id}.json.gz"
        assert archive_file.exists()

        # Verify contents can be perfectly decompressed and loaded
        with gzip.open(archive_file, "rt", encoding="utf-8") as f:
            data = json.load(f)
            assert data["session_id"] == old_session.session_id
            assert data["name"] == "Very Old Session"
            assert len(data["messages"]) == 1
            assert data["messages"][0]["content"] == "What is the capital of France?"
