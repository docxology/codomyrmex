"""Integration tests for Hermes gateway SQLite session concurrency."""

import threading
import time
from pathlib import Path

from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore


def write_worker(db_path: str, thread_index: int, iterations: int) -> None:
    """Worker that continuously opens the DB and writes to a session."""
    with SQLiteSessionStore(db_path) as store:
        session = HermesSession(name=f"Thread_{thread_index}")
        # Insert initial
        store.save(session)
        for i in range(iterations):
            session.add_message("user", f"Message {i} from thread {thread_index}")
            store.save(session)
            time.sleep(0.001)


def test_sqlite_concurrent_writes_wal(tmp_path: Path) -> None:
    """Ensure WAL mode allows concurrent threads to write without 'database is locked'."""
    db_file = tmp_path / "concurrent_state.db"

    # Initialize schema
    with SQLiteSessionStore(db_file) as _:
        pass

    threads = []
    # 10 threads doing 20 iterations each
    for i in range(10):
        t = threading.Thread(target=write_worker, args=(str(db_file), i, 20))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=5.0)
        assert not t.is_alive(), "Thread blocked on database lock"

    # Verify records
    with SQLiteSessionStore(db_file) as store:
        sessions = store.list_sessions()
        assert len(sessions) == 10

        for s_id in sessions:
            session = store.load(s_id)
            assert session is not None
            # Initial create + 20 iterations = 20 messages (initial doesn't add a message)
            assert session.message_count == 20
