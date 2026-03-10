"""Tests for ObsidianMemoryBridge — strictly zero-mock."""

import tempfile

import pytest

from codomyrmex.agentic_memory.memory import VectorStoreMemory
from codomyrmex.agentic_memory.obsidian.crud import create_note, read_note
from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault
from codomyrmex.agentic_memory.obsidian_bridge import ObsidianMemoryBridge
from codomyrmex.agentic_memory.stores import InMemoryStore


@pytest.fixture
def temp_vault():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = ObsidianVault(tmpdir)
        yield vault


@pytest.fixture
def memory():
    from codomyrmex.vector_store import create_vector_store
    vs = create_vector_store(backend="memory")
    return VectorStoreMemory(store=InMemoryStore(), vector_store=vs)


@pytest.fixture
def bridge(temp_vault, memory):
    return ObsidianMemoryBridge(temp_vault, memory, export_folder="Agent")


class TestObsidianMemoryBridge:
    def test_ingest_new_note(self, temp_vault, bridge, memory):
        # Create a new note unlinked to memory
        create_note(temp_vault, "Note1", content="Agent task", frontmatter={"tags": ["ai"]})

        stats = bridge.ingest_vault()
        assert stats["added"] == 1
        assert stats["updated"] == 0

        # Verify it got an ID
        note = read_note(temp_vault, "Note1")
        agent_id = note.frontmatter.get("agentic_id")
        assert agent_id is not None

        # Verify it is in memory
        mem = memory.store.get(agent_id)
        assert mem is not None
        assert mem.content == "Agent task"
        assert mem.metadata["source"] == "obsidian"

    def test_ingest_update_existing_note(self, temp_vault, bridge, memory):
        # Create a memory first
        mem = memory.remember("Old Content")

        # Create a note mapped to it
        create_note(
            temp_vault,
            "Note2",
            content="New Content",
            frontmatter={"agentic_id": mem.id}
        )

        stats = bridge.ingest_vault()
        assert stats["updated"] == 1

        # Memory should be updated
        updated_mem = memory.store.get(mem.id)
        assert updated_mem.content == "New Content"

    def test_export_memories(self, temp_vault, bridge, memory):
        # Add a memory not from obsidian
        mem1 = memory.remember("This is a synthesized insight.")
        mem1.metadata["source"] = "agentic_memory"
        memory.store.save(mem1)

        # Add a memory already from obsidian (should be skipped)
        mem2 = memory.remember("From obsidian initially")
        mem2.metadata["source"] = "obsidian"
        memory.store.save(mem2)

        stats = bridge.export_memories()

        assert stats["created"] == 1
        assert stats["skipped"] >= 1

        # The file should exist in the vault
        notes = temp_vault.list_notes()
        assert any("Agent/" in n for n in notes)

        # It should have the right frontmatter
        exported = next(n for n in notes if "Agent/" in n)
        note = read_note(temp_vault, exported)
        assert note.frontmatter["agentic_id"] == mem1.id
        assert note.content == "This is a synthesized insight."

    def test_sync(self, temp_vault, bridge, memory):
        memory.remember("Memory native stuff")
        create_note(temp_vault, "Obsidian_stuff", content="Obsidian native")

        stats = bridge.sync()
        assert stats["export"]["created"] == 1
        assert stats["ingest"]["added"] == 1
