"""Tests for JSONFileStore — strictly zero-mock.

Covers save, get, delete, list_all, persistence across instances,
thread safety, and edge cases (empty file, list-format JSON, missing file).
"""

import json
import os
import tempfile
import threading

import pytest

from codomyrmex.agentic_memory.models import Memory, MemoryImportance, MemoryType
from codomyrmex.agentic_memory.stores import JSONFileStore


@pytest.fixture
def json_store():
    """Provide a JSONFileStore backed by a temp file that is cleaned up."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        path = tf.name
    # Ensure file exists (empty) so JSONFileStore doesn't fail on first load
    with open(path, "w") as f:
        json.dump([], f)
    store = JSONFileStore(path)
    yield store
    if os.path.exists(path):
        os.remove(path)


class TestJSONFileStoreBasic:
    """Core CRUD operations."""

    def test_save_and_get(self, json_store):
        """Should persist and retrieve a memory."""
        m = Memory(
            id="test-1",
            content="Hello JSON",
            memory_type=MemoryType.EPISODIC,
            importance=MemoryImportance.HIGH,
            metadata={"source": "test"},
            tags=["json", "test"],
        )
        json_store.save(m)

        retrieved = json_store.get("test-1")
        assert retrieved is not None
        assert retrieved.id == "test-1"
        assert retrieved.content == "Hello JSON"
        assert retrieved.memory_type == MemoryType.EPISODIC
        assert retrieved.importance == MemoryImportance.HIGH
        assert retrieved.metadata == {"source": "test"}
        assert retrieved.tags == ["json", "test"]

    def test_get_nonexistent(self, json_store):
        """Should return None for unknown ID."""
        assert json_store.get("nonexistent") is None

    def test_upsert(self, json_store):
        """Should overwrite existing entry on save."""
        m = Memory(id="upsert-1", content="Original")
        json_store.save(m)

        m.content = "Updated"
        json_store.save(m)

        retrieved = json_store.get("upsert-1")
        assert retrieved is not None
        assert retrieved.content == "Updated"

    def test_delete_existing(self, json_store):
        """Should delete and return True."""
        m = Memory(id="del-1", content="To delete")
        json_store.save(m)

        assert json_store.delete("del-1") is True
        assert json_store.get("del-1") is None

    def test_delete_nonexistent(self, json_store):
        """Should return False when ID not found."""
        assert json_store.delete("ghost") is False

    def test_list_all_empty(self, json_store):
        """Should return empty list for fresh store."""
        assert json_store.list_all() == []

    def test_list_all_multiple(self, json_store):
        """Should return all stored memories."""
        json_store.save(Memory(id="a", content="First"))
        json_store.save(Memory(id="b", content="Second"))
        json_store.save(Memory(id="c", content="Third"))

        all_mems = json_store.list_all()
        assert len(all_mems) == 3
        ids = {m.id for m in all_mems}
        assert ids == {"a", "b", "c"}


class TestJSONFileStorePersistence:
    """Data survives across store instances (reads from disk)."""

    def test_reload_from_disk(self, json_store):
        """New instance should load previously saved data."""
        json_store.save(Memory(id="persist-1", content="Persisted"))
        # Create a new store instance pointing to same file
        new_store = JSONFileStore(json_store._path)
        retrieved = new_store.get("persist-1")
        assert retrieved is not None
        assert retrieved.content == "Persisted"

    def test_delete_persists(self, json_store):
        """Deletion should be reflected in new store instance."""
        json_store.save(Memory(id="gone", content="Will be deleted"))
        json_store.delete("gone")

        new_store = JSONFileStore(json_store._path)
        assert new_store.get("gone") is None

    def test_list_format_json(self):
        """Should handle JSON files stored as a list of dicts (legacy format)."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            path = tf.name
        try:
            # Write legacy list format
            with open(path, "w") as f:
                json.dump(
                    [
                        {"id": "x", "content": "Legacy entry"},
                        {"id": "y", "content": "Another"},
                    ],
                    f,
                )
            store = JSONFileStore(path)
            all_mems = store.list_all()
            assert len(all_mems) == 2
            ids = {m.id for m in all_mems}
            assert ids == {"x", "y"}
        finally:
            os.remove(path)

    def test_dict_format_json(self):
        """Should handle JSON files stored as a dict keyed by ID."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            path = tf.name
        try:
            with open(path, "w") as f:
                json.dump(
                    {
                        "k1": {"id": "k1", "content": "Dict entry"},
                    },
                    f,
                )
            store = JSONFileStore(path)
            retrieved = store.get("k1")
            assert retrieved is not None
            assert retrieved.content == "Dict entry"
        finally:
            os.remove(path)


class TestJSONFileStoreConcurrency:
    """Thread safety for concurrent writes."""

    def test_concurrent_saves(self, json_store):
        """Multiple threads saving should not corrupt data."""
        errors = []

        def save_memory(idx: int):
            try:
                for _ in range(5):
                    json_store.save(
                        Memory(id=f"thread-{idx}", content=f"From thread {idx}")
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=save_memory, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors, f"Thread errors: {errors}"
        all_mems = json_store.list_all()
        assert len(all_mems) == 10


class TestJSONFileStoreEdgeCases:
    """Edge cases and boundary conditions."""

    def test_empty_content(self, json_store):
        """Should handle empty content string."""
        m = Memory(id="empty", content="")
        json_store.save(m)
        retrieved = json_store.get("empty")
        assert retrieved is not None
        assert retrieved.content == ""

    def test_special_characters_content(self, json_store):
        """Should handle content with special characters."""
        special = 'Content with "quotes", \\backslashes\\, and\nnewlines\tand\ttabs'
        m = Memory(id="special", content=special)
        json_store.save(m)
        retrieved = json_store.get("special")
        assert retrieved is not None
        assert retrieved.content == special

    def test_unicode_content(self, json_store):
        """Should handle unicode characters."""
        unicode_content = "Hello 世界 🎉 Привет مرحبا"
        m = Memory(id="unicode", content=unicode_content)
        json_store.save(m)
        retrieved = json_store.get("unicode")
        assert retrieved is not None
        assert retrieved.content == unicode_content

    def test_large_metadata(self, json_store):
        """Should handle large metadata dict."""
        large_meta = {f"key_{i}": f"value_{i}" for i in range(100)}
        m = Memory(id="large-meta", content="Has lots of metadata", metadata=large_meta)
        json_store.save(m)
        retrieved = json_store.get("large-meta")
        assert retrieved is not None
        assert len(retrieved.metadata) == 100

    def test_memory_access_tracking(self, json_store):
        """get() should NOT increment access_count (unlike SQLiteStore)."""
        m = Memory(id="access-test", content="Track me")
        json_store.save(m)

        retrieved = json_store.get("access-test")
        assert retrieved is not None
        # JSONFileStore.get() does not call access() — it just deserializes
        # This is intentional: JSON is read-only from disk, no side effects
        assert retrieved.access_count == 0

    def test_create_parent_directory(self):
        """Should create parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = os.path.join(tmpdir, "sub", "dir", "store.json")
            store = JSONFileStore(nested_path)
            store.save(Memory(id="nested", content="In nested dir"))
            assert os.path.exists(nested_path)

            # Verify data persists
            retrieved = store.get("nested")
            assert retrieved is not None
            assert retrieved.content == "In nested dir"

    def test_malformed_json_starts_empty(self):
        """Should start with empty data when JSON file is corrupted."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            path = tf.name
        try:
            with open(path, "w") as f:
                f.write("{not valid json at all!!!")
            store = JSONFileStore(path)
            assert store.list_all() == []
            # Should be usable after recovery
            store.save(Memory(id="after-corrupt", content="Still works"))
            retrieved = store.get("after-corrupt")
            assert retrieved is not None
            assert retrieved.content == "Still works"
        finally:
            os.remove(path)

    def test_list_entries_missing_id_key(self):
        """Should skip list entries that lack an 'id' key."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            path = tf.name
        try:
            with open(path, "w") as f:
                json.dump(
                    [
                        {"id": "valid", "content": "OK"},
                        {"content": "no id field"},  # missing id
                        "not a dict",  # wrong type
                    ],
                    f,
                )
            store = JSONFileStore(path)
            all_mems = store.list_all()
            assert len(all_mems) == 1
            assert all_mems[0].id == "valid"
        finally:
            os.remove(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
