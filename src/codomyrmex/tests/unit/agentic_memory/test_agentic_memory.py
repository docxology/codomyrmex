"""
Tests for Agentic Memory Module
"""

import pytest
from codomyrmex.agentic_memory import (
    MemoryType,
    MemoryImportance,
    Memory,
    RetrievalResult,
    InMemoryStore,
    AgentMemory,
    ConversationMemory,
    KnowledgeMemory,
)


class TestMemory:
    """Tests for Memory."""
    
    def test_create(self):
        """Should create memory."""
        m = Memory(id="1", content="Test content")
        assert m.id == "1"
        assert m.memory_type == MemoryType.EPISODIC
    
    def test_access(self):
        """Should track access."""
        m = Memory(id="1", content="Test")
        assert m.access_count == 0
        
        m.access()
        assert m.access_count == 1
    
    def test_to_dict(self):
        """Should convert to dict."""
        m = Memory(id="1", content="Test")
        d = m.to_dict()
        assert d["id"] == "1"
        assert d["content"] == "Test"
    
    def test_from_dict(self):
        """Should create from dict."""
        d = {"id": "1", "content": "Test", "memory_type": "semantic"}
        m = Memory.from_dict(d)
        assert m.id == "1"
        assert m.memory_type == MemoryType.SEMANTIC


class TestInMemoryStore:
    """Tests for InMemoryStore."""
    
    def test_save_and_get(self):
        """Should save and retrieve."""
        store = InMemoryStore()
        m = Memory(id="1", content="Test")
        store.save(m)
        
        retrieved = store.get("1")
        assert retrieved.content == "Test"
    
    def test_delete(self):
        """Should delete memory."""
        store = InMemoryStore()
        store.save(Memory(id="1", content="Test"))
        
        assert store.delete("1") is True
        assert store.get("1") is None
    
    def test_list_all(self):
        """Should list all memories."""
        store = InMemoryStore()
        store.save(Memory(id="1", content="A"))
        store.save(Memory(id="2", content="B"))
        
        assert len(store.list_all()) == 2


class TestAgentMemory:
    """Tests for AgentMemory."""
    
    def test_remember(self):
        """Should store memory."""
        agent = AgentMemory()
        m = agent.remember("User prefers Python")
        
        assert m.content == "User prefers Python"
        assert agent.memory_count == 1
    
    def test_recall(self):
        """Should recall relevant memories."""
        agent = AgentMemory()
        agent.remember("User prefers Python")
        agent.remember("User likes dark themes")
        agent.remember("User is learning ML")
        
        results = agent.recall("programming language", k=2)
        assert len(results) <= 2
        assert all(isinstance(r, RetrievalResult) for r in results)
    
    def test_recall_with_filter(self):
        """Should filter by type."""
        agent = AgentMemory()
        agent.remember("Fact 1", memory_type=MemoryType.SEMANTIC)
        agent.remember("Experience 1", memory_type=MemoryType.EPISODIC)
        
        results = agent.recall("", memory_type=MemoryType.SEMANTIC)
        assert all(r.memory.memory_type == MemoryType.SEMANTIC for r in results)
    
    def test_forget(self):
        """Should forget memory."""
        agent = AgentMemory()
        m = agent.remember("Temporary")
        
        assert agent.forget(m.id) is True
        assert agent.memory_count == 0
    
    def test_get_context(self):
        """Should get formatted context."""
        agent = AgentMemory()
        agent.remember("Python is great")
        
        context = agent.get_context("programming")
        assert "Python" in context
    
    def test_importance_filter(self):
        """Should filter by importance."""
        agent = AgentMemory()
        agent.remember("Low priority", importance=MemoryImportance.LOW)
        agent.remember("High priority", importance=MemoryImportance.HIGH)
        
        results = agent.recall("priority", min_importance=MemoryImportance.HIGH)
        assert all(r.memory.importance.value >= MemoryImportance.HIGH.value for r in results)


class TestConversationMemory:
    """Tests for ConversationMemory."""
    
    def test_add_turn(self):
        """Should add conversation turn."""
        mem = ConversationMemory()
        m = mem.add_turn("user", "Hello!", turn_number=1)
        
        assert m.content == "Hello!"
        assert m.metadata["role"] == "user"
        assert m.metadata["turn"] == 1


class TestKnowledgeMemory:
    """Tests for KnowledgeMemory."""
    
    def test_add_fact(self):
        """Should add fact."""
        mem = KnowledgeMemory()
        m = mem.add_fact("Python was released in 1991", source="Wikipedia")
        
        assert m.memory_type == MemoryType.SEMANTIC
        assert m.metadata["source"] == "Wikipedia"


class TestRetrievalResult:
    """Tests for RetrievalResult."""
    
    def test_combined_score(self):
        """Should compute combined score."""
        m = Memory(id="1", content="Test")
        r = RetrievalResult(
            memory=m,
            relevance_score=0.8,
            recency_score=0.5,
            importance_score=0.7,
        )
        
        score = r.combined_score
        assert 0 <= score <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
