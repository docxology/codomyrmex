"""Tests for SQLiteStore — strictly zero-mock."""

import os
import tempfile

import pytest

from codomyrmex.agentic_memory.models import Memory, MemoryImportance, MemoryType
from codomyrmex.agentic_memory.sqlite_store import SQLiteStore


@pytest.fixture
def sqlite_store():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name
    store = SQLiteStore(db_path=db_path)
    yield store
    if os.path.exists(db_path):
        os.remove(db_path)


class TestSQLiteStore:
    def test_save_and_get(self, sqlite_store):
        m = Memory(
            id="1",
            content="Testing sqlite",
            memory_type=MemoryType.EPISODIC,
            importance=MemoryImportance.HIGH,
            metadata={"source": "test"},
            tags=["test", "sqlite"],
        )
        sqlite_store.save(m)

        retrieved = sqlite_store.get("1")
        assert retrieved is not None
        assert retrieved.id == "1"
        assert retrieved.content == "Testing sqlite"
        assert retrieved.memory_type == MemoryType.EPISODIC
        assert retrieved.importance == MemoryImportance.HIGH
        assert retrieved.metadata == {"source": "test"}
        assert retrieved.tags == ["test", "sqlite"]
        assert retrieved.access_count == 1  # get() increments access_count

    def test_get_nonexistent(self, sqlite_store):
        assert sqlite_store.get("invalid") is None

    def test_upsert(self, sqlite_store):
        m = Memory(id="1", content="Initial")
        sqlite_store.save(m)

        m.content = "Updated"
        sqlite_store.save(m)

        retrieved = sqlite_store.get("1")
        assert retrieved.content == "Updated"

    def test_delete(self, sqlite_store):
        m = Memory(id="1", content="To be deleted")
        sqlite_store.save(m)

        assert sqlite_store.delete("1") is True
        assert sqlite_store.get("1") is None
        assert sqlite_store.delete("1") is False

    def test_list_all(self, sqlite_store):
        m1 = Memory(id="1", content="First")
        m2 = Memory(id="2", content="Second")
        sqlite_store.save(m1)
        sqlite_store.save(m2)

        memories = sqlite_store.list_all()
        assert len(memories) == 2
        ids = {mem.id for mem in memories}
        assert "1" in ids
        assert "2" in ids
