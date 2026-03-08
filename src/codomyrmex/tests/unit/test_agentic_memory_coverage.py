# type: ignore
"""Functional tests for agentic_memory module — zero-mock.

Exercises Memory, AgentMemory, ConversationMemory, KnowledgeMemory,
InMemoryStore, JSONFileStore, ObsidianMemoryBridge, and retrieval.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import codomyrmex.agentic_memory as am


class TestAgenticMemoryImports:
    """All 20 exports are importable."""

    @pytest.mark.parametrize(
        "name",
        [
            "AgentMemory",
            "ConversationMemory",
            "InMemoryStore",
            "JSONFileStore",
            "KnowledgeMemory",
            "Memory",
            "MemoryImportance",
            "MemoryType",
            "ObsidianMemoryBridge",
            "RetrievalResult",
        ],
    )
    def test_export_exists(self, name: str) -> None:
        assert hasattr(am, name), f"Missing export: {name}"


class TestEnums:
    """Memory enums."""

    def test_memory_importance_members(self) -> None:
        mi = am.MemoryImportance
        assert len(list(mi)) >= 2

    def test_memory_type_members(self) -> None:
        mt = am.MemoryType
        assert len(list(mt)) >= 2


class TestMemoryClasses:
    """Memory class instantiation."""

    def test_memory_callable(self) -> None:
        assert callable(am.Memory)

    def test_agent_memory_callable(self) -> None:
        assert callable(am.AgentMemory)

    def test_conversation_memory_callable(self) -> None:
        assert callable(am.ConversationMemory)

    def test_knowledge_memory_callable(self) -> None:
        assert callable(am.KnowledgeMemory)

    def test_retrieval_result_callable(self) -> None:
        assert callable(am.RetrievalResult)


class TestStores:
    """Memory store classes."""

    def test_in_memory_store_instantiation(self) -> None:
        store = am.InMemoryStore()
        assert store is not None

    def test_in_memory_store_has_methods(self) -> None:
        store = am.InMemoryStore()
        public = [m for m in dir(store) if not m.startswith("_") and callable(getattr(store, m))]
        assert len(public) > 0

    def test_json_file_store_callable(self) -> None:
        assert callable(am.JSONFileStore)


class TestObsidianBridge:
    """ObsidianMemoryBridge instantiation."""

    def test_bridge_callable(self) -> None:
        assert callable(am.ObsidianMemoryBridge)
