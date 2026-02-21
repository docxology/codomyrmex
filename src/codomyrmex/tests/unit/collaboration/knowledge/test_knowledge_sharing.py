"""Tests for Sprint 28: Cross-Agent Knowledge Sharing.

Covers KnowledgeEntry, SharedMemoryPool (namespace isolation, ACL,
global search, conflict resolution), and KnowledgeRouter (routing,
expertise matching).
"""

import time
import pytest

from codomyrmex.collaboration.knowledge.models import (
    AccessLevel,
    ConflictStrategy,
    ExpertiseProfile,
    KnowledgeEntry,
    NamespaceACL,
    QueryResult,
)
from codomyrmex.collaboration.knowledge.shared_pool import SharedMemoryPool
from codomyrmex.collaboration.knowledge.knowledge_router import KnowledgeRouter


# ─── Models ───────────────────────────────────────────────────────────

class TestModels:

    def test_knowledge_entry_cite(self):
        entry = KnowledgeEntry(key="k", value="v", source_agent="a")
        assert entry.citation_count == 0
        entry.cite()
        assert entry.citation_count == 1

    def test_namespace_acl_owner_access(self):
        acl = NamespaceACL(owner="agent-a")
        assert acl.can_read("agent-a") is True
        assert acl.can_write("agent-a") is True

    def test_namespace_acl_read_only(self):
        acl = NamespaceACL(owner="agent-a", permissions={"agent-b": AccessLevel.READ})
        assert acl.can_read("agent-b") is True
        assert acl.can_write("agent-b") is False


# ─── SharedMemoryPool ────────────────────────────────────────────────

class TestSharedMemoryPool:

    def test_namespace_isolation(self):
        """Agent A's entries are not visible to Agent B without access."""
        pool = SharedMemoryPool()
        pool.create_namespace("agent-a")
        pool.create_namespace("agent-b")
        pool.put("agent-a", "secret", "value-a", domain="testing")

        # agent-b can't read agent-a's namespace
        result = pool.get("agent-b", "secret", namespace="agent-a")
        assert result is None

    def test_owner_can_read_write(self):
        pool = SharedMemoryPool()
        pool.create_namespace("agent-a")
        pool.put("agent-a", "key", "value")
        entry = pool.get("agent-a", "key")
        assert entry is not None
        assert entry.value == "value"

    def test_global_search_cross_namespace(self):
        pool = SharedMemoryPool()
        pool.create_namespace("agent-a")
        pool.create_namespace("agent-b")
        pool.put("agent-a", "pytest-tip", "use fixtures", domain="testing", tags=["pytest"])
        pool.put("agent-b", "deploy-tip", "use containers", domain="ops", tags=["deploy"])

        results = pool.search_global(["pytest"])
        assert len(results) == 1
        assert results[0].key == "pytest-tip"

    def test_conflict_last_write_wins(self):
        pool = SharedMemoryPool(conflict_strategy=ConflictStrategy.LAST_WRITE_WINS)
        pool.create_namespace("a")
        pool.put("a", "key", "v1")
        pool.put("a", "key", "v2")
        entry = pool.get("a", "key")
        assert entry.value == "v2"

    def test_acl_enforcement(self):
        pool = SharedMemoryPool()
        pool.create_namespace("owner")
        pool.grant_access("owner", "reader", AccessLevel.READ)
        pool.put("owner", "data", "secret")

        # Reader can read
        entry = pool.get("reader", "data", namespace="owner")
        assert entry is not None

        # Reader can't write (needs own namespace)
        wrote = pool.put("reader", "hack", "bad")
        assert wrote is False  # reader has no own namespace

    def test_namespace_stats(self):
        pool = SharedMemoryPool()
        pool.create_namespace("a")
        pool.put("a", "k1", "v1", domain="testing")
        pool.put("a", "k2", "v2", domain="testing")
        stats = pool.namespace_stats("a")
        assert stats.entry_count == 2
        assert stats.domain_counts["testing"] == 2


# ─── KnowledgeRouter ─────────────────────────────────────────────────

class TestKnowledgeRouter:

    def test_route_to_correct_expert(self):
        pool = SharedMemoryPool()
        router = KnowledgeRouter(pool=pool)
        router.register_expert(ExpertiseProfile(
            agent_id="tester",
            domains={"testing": 0.9},
            tags=["pytest", "coverage", "fixtures"],
        ))
        router.register_expert(ExpertiseProfile(
            agent_id="deployer",
            domains={"deployment": 0.8},
            tags=["docker", "k8s"],
        ))

        agent_id, confidence = router.route("pytest fixtures for testing")
        assert agent_id == "tester"
        assert confidence > 0

    def test_route_empty_experts(self):
        router = KnowledgeRouter()
        agent_id, confidence = router.route("anything")
        assert agent_id == ""
        assert confidence == 0.0

    def test_query_returns_results(self):
        pool = SharedMemoryPool()
        pool.create_namespace("tester")
        pool.put("tester", "tip-1", "Use parametrize", domain="testing", tags=["pytest"])

        router = KnowledgeRouter(pool=pool)
        router.register_expert(ExpertiseProfile(
            agent_id="tester",
            domains={"testing": 0.9},
            tags=["pytest"],
        ))

        result = router.query("pytest")
        assert isinstance(result, QueryResult)
        assert len(result.entries) >= 1

    def test_suggest_experts(self):
        router = KnowledgeRouter()
        router.register_expert(ExpertiseProfile(
            agent_id="a", domains={"testing": 0.9}, tags=["pytest"],
        ))
        router.register_expert(ExpertiseProfile(
            agent_id="b", domains={"ops": 0.7}, tags=["docker"],
        ))
        suggestions = router.suggest_experts("pytest testing", n=2)
        assert len(suggestions) >= 1
        assert suggestions[0][0] == "a"
