"""Tests for memory integration: stores, AgentMemory, VectorStoreMemory, UserProfile.

All tests use real objects and real file I/O — zero mocks.
"""

import threading
import uuid

import pytest

from codomyrmex.agentic_memory.models import Memory, MemoryImportance, MemoryType
from codomyrmex.agentic_memory.stores import InMemoryStore, JSONFileStore
from codomyrmex.agentic_memory.memory import AgentMemory, VectorStoreMemory
from codomyrmex.agentic_memory.user_profile import UserProfile


def _make_memory(content: str = "test", importance: MemoryImportance = MemoryImportance.MEDIUM) -> Memory:
    """Helper: create a Memory with auto-generated id."""
    return Memory(id=f"mem_{uuid.uuid4().hex[:8]}", content=content, importance=importance)


# ── JSONFileStore round-trip ──────────────────────────────────────────


class TestJSONFileStore:

    def test_save_load_round_trip(self, tmp_path):
        path = str(tmp_path / "memories.json")
        store = JSONFileStore(path)
        mem = _make_memory("Hello world", MemoryImportance.HIGH)
        store.save(mem)

        # Reload from disk
        store2 = JSONFileStore(path)
        loaded = store2.get(mem.id)
        assert loaded is not None
        assert loaded.content == "Hello world"
        assert loaded.importance is MemoryImportance.HIGH

    def test_list_all(self, tmp_path):
        path = str(tmp_path / "memories.json")
        store = JSONFileStore(path)
        for i in range(5):
            store.save(_make_memory(f"Item {i}"))
        assert len(store.list_all()) == 5

    def test_delete(self, tmp_path):
        path = str(tmp_path / "memories.json")
        store = JSONFileStore(path)
        mem = _make_memory("to delete")
        store.save(mem)
        assert store.delete(mem.id) is True
        assert store.get(mem.id) is None
        assert store.delete("nonexistent") is False

    def test_concurrent_writes(self, tmp_path):
        """Thread-safe: concurrent writes via threading.Lock."""
        path = str(tmp_path / "concurrent.json")
        store = JSONFileStore(path)
        errors: list[Exception] = []

        def writer(n):
            try:
                for i in range(10):
                    store.save(_make_memory(f"thread-{n}-item-{i}"))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(t,)) for t in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Concurrent writes failed: {errors}"
        assert len(store.list_all()) == 40


# ── InMemoryStore ─────────────────────────────────────────────────────


class TestInMemoryStore:

    def test_basic_crud(self):
        store = InMemoryStore()
        mem = _make_memory("test")
        store.save(mem)
        assert store.get(mem.id) is not None
        assert len(store.list_all()) == 1
        assert store.delete(mem.id) is True
        assert len(store.list_all()) == 0


# ── AgentMemory ──────────────────────────────────────────────────────


class TestAgentMemory:

    def test_add_and_search(self):
        agent_mem = AgentMemory()
        agent_mem.add(content="Paris is the capital of France", importance=MemoryImportance.HIGH)
        results = agent_mem.search("Paris")
        assert len(results) >= 1
        assert any("Paris" in r.memory.content for r in results)

    def test_add_returns_memory(self):
        agent_mem = AgentMemory()
        mem = agent_mem.add(content="test content")
        assert isinstance(mem, Memory)
        assert mem.content == "test content"


# ── VectorStoreMemory ────────────────────────────────────────────────


class TestVectorStoreMemory:

    def test_auto_creates_store(self):
        """VectorStoreMemory with no store creates InMemoryStore internally."""
        vsm = VectorStoreMemory()
        assert vsm.store is not None

    def test_add_and_recall(self):
        vsm = VectorStoreMemory()
        vsm.add(content="Python is a programming language", importance=MemoryImportance.HIGH)
        vsm.add(content="JavaScript runs in browsers", importance=MemoryImportance.MEDIUM)
        results = vsm.search("programming")
        assert len(results) >= 1


# ── UserProfile ──────────────────────────────────────────────────────


class TestUserProfile:

    def test_create_and_save(self, tmp_path):
        path = tmp_path / "profile.json"
        profile = UserProfile(preferences={"theme": "dark"})
        profile.save(path)
        assert path.exists()

    def test_load_round_trip(self, tmp_path):
        path = tmp_path / "profile.json"
        original = UserProfile(preferences={"lang": "en"}, history_summary="test session")
        original.save(path)

        loaded = UserProfile.load(path)
        assert loaded.preferences["lang"] == "en"
        assert loaded.history_summary == "test session"

    def test_load_default_when_missing(self, tmp_path):
        """Loading from a non-existent file returns a default profile."""
        path = tmp_path / "nonexistent.json"
        profile = UserProfile.load(path)
        assert isinstance(profile, UserProfile)
        assert profile.preferences == {}

    def test_set_and_get_preference(self):
        profile = UserProfile()
        profile.set_preference("theme", "dark")
        assert profile.get_preference("theme") == "dark"
        assert profile.get_preference("missing", "default") == "default"

    def test_to_context_string(self):
        profile = UserProfile(preferences={"lang": "en"})
        ctx = profile.to_context_string()
        assert "lang=en" in ctx
