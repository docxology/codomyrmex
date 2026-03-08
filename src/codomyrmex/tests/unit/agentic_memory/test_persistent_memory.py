"""Tests for Persistent Memory."""

import os
import tempfile

from codomyrmex.agentic_memory.memory import AgentMemory
from codomyrmex.agentic_memory.sqlite_store import SQLiteStore


class TestPersistentMemory:
    def test_sqlite_persistence(self):
        """Should persist memories across different store instances connected to the same DB."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_memory.db")

            # First instantiation
            store1 = SQLiteStore(db_path)
            agent1 = AgentMemory(store1)
            agent1.remember("The secret code is 42")
            assert agent1.memory_count == 1

            # Second instantiation (simulating a restart)
            store2 = SQLiteStore(db_path)
            agent2 = AgentMemory(store2)

            # The memory should persist
            assert agent2.memory_count == 1
            results = agent2.search("secret")
            assert len(results) == 1
            assert "42" in results[0].memory.content
