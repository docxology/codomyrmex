"""Shared memory pool with namespace isolation.

Multi-agent MemoryStore with per-agent namespaces, ACL enforcement,
cross-namespace global search, and configurable conflict resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.collaboration.knowledge.models import (
    AccessLevel,
    ConflictStrategy,
    KnowledgeEntry,
    NamespaceACL,
)


@dataclass
class NamespaceStats:
    """Statistics for a namespace.

    Attributes:
        agent_id: Namespace owner.
        entry_count: Number of entries.
        domain_counts: Count per domain.
        total_citations: Sum of citations.
    """

    agent_id: str
    entry_count: int = 0
    domain_counts: dict[str, int] = field(default_factory=dict)
    total_citations: int = 0


class SharedMemoryPool:
    """Multi-agent knowledge store with namespace isolation.

    Each agent gets an isolated namespace. Cross-namespace search
    and conflict resolution are supported with ACL enforcement.

    Example::

        pool = SharedMemoryPool()
        pool.create_namespace("agent-a")
        pool.put("agent-a", "best_practice", "Always test", domain="testing")
        results = pool.search_global(["test"])
    """

    def __init__(
        self,
        conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS,
    ) -> None:
        self._namespaces: dict[str, dict[str, KnowledgeEntry]] = {}
        self._acls: dict[str, NamespaceACL] = {}
        self._conflict_strategy = conflict_strategy

    def create_namespace(
        self,
        agent_id: str,
        permissions: dict[str, AccessLevel] | None = None,
    ) -> None:
        """Create an isolated namespace for an agent.

        Args:
            agent_id: Agent identifier (becomes namespace owner).
            permissions: Optional ACL for other agents.
        """
        if agent_id not in self._namespaces:
            self._namespaces[agent_id] = {}
            self._acls[agent_id] = NamespaceACL(
                owner=agent_id,
                permissions=permissions or {},
            )

    @property
    def namespace_count(self) -> int:
        """Number of registered namespaces."""
        return len(self._namespaces)

    def put(
        self,
        agent_id: str,
        key: str,
        value: Any,
        domain: str = "",
        tags: list[str] | None = None,
    ) -> bool:
        """Store a knowledge entry in an agent's namespace.

        Args:
            agent_id: Agent writing the entry.
            key: Entry key.
            value: Entry value.
            domain: Knowledge domain.
            tags: Searchable tags.

        Returns:
            True if written, False if ACL denied.
        """
        # Find which namespace to write to
        target_ns = agent_id
        if target_ns not in self._namespaces:
            return False

        acl = self._acls[target_ns]
        if not acl.can_write(agent_id):
            return False

        entry = KnowledgeEntry(
            key=key,
            value=value,
            source_agent=agent_id,
            domain=domain,
            tags=tags or [],
        )

        existing = self._namespaces[target_ns].get(key)
        if existing is not None:
            entry = self._resolve_conflict(existing, entry)

        self._namespaces[target_ns][key] = entry
        return True

    def get(self, agent_id: str, key: str, namespace: str | None = None) -> KnowledgeEntry | None:
        """Retrieve a knowledge entry.

        Args:
            agent_id: Agent requesting the entry.
            key: Entry key.
            namespace: Namespace to read from (defaults to agent's own).

        Returns:
            KnowledgeEntry if found and allowed, None otherwise.
        """
        target_ns = namespace or agent_id
        if target_ns not in self._namespaces:
            return None

        acl = self._acls[target_ns]
        if not acl.can_read(agent_id):
            return None

        entry = self._namespaces[target_ns].get(key)
        if entry is not None:
            entry.cite()
        return entry

    def delete(self, agent_id: str, key: str) -> bool:
        """Delete an entry from an agent's namespace.

        Args:
            agent_id: Agent requesting deletion.
            key: Entry key.

        Returns:
            True if deleted, False if not found or not allowed.
        """
        if agent_id not in self._namespaces:
            return False

        acl = self._acls[agent_id]
        if not acl.can_write(agent_id):
            return False

        return self._namespaces[agent_id].pop(key, None) is not None

    def search_global(
        self,
        query_terms: list[str],
        domains: list[str] | None = None,
        requesting_agent: str = "",
    ) -> list[KnowledgeEntry]:
        """Search across all namespaces.

        Args:
            query_terms: Terms to match in tags, domain, or key.
            domains: Optional domain filter.
            requesting_agent: Agent performing the search (for ACL check).

        Returns:
            List of matching entries from all accessible namespaces.
        """
        results: list[KnowledgeEntry] = []
        terms_lower = [t.lower() for t in query_terms]

        for ns_id, entries in self._namespaces.items():
            # Check read access
            if requesting_agent:
                acl = self._acls.get(ns_id)
                if acl and not acl.can_read(requesting_agent):
                    continue

            for entry in entries.values():
                # Domain filter
                if domains and entry.domain not in domains:
                    continue

                # Term matching: check key, domain, tags
                searchable = (
                    [entry.key.lower(), entry.domain.lower()]
                    + [t.lower() for t in entry.tags]
                )
                if any(term in s for term in terms_lower for s in searchable):
                    results.append(entry)

        # Sort by citation count descending
        results.sort(key=lambda e: e.citation_count, reverse=True)
        return results

    def namespace_stats(self, agent_id: str) -> NamespaceStats | None:
        """Get statistics for a namespace."""
        entries = self._namespaces.get(agent_id)
        if entries is None:
            return None

        domain_counts: dict[str, int] = {}
        total_citations = 0
        for e in entries.values():
            if e.domain:
                domain_counts[e.domain] = domain_counts.get(e.domain, 0) + 1
            total_citations += e.citation_count

        return NamespaceStats(
            agent_id=agent_id,
            entry_count=len(entries),
            domain_counts=domain_counts,
            total_citations=total_citations,
        )

    def grant_access(self, owner: str, target_agent: str, level: AccessLevel) -> bool:
        """Grant access to another agent's namespace.

        Args:
            owner: Namespace owner.
            target_agent: Agent to grant access to.
            level: Access level to grant.

        Returns:
            True if granted, False if namespace not found.
        """
        acl = self._acls.get(owner)
        if acl is None:
            return False
        acl.permissions[target_agent] = level
        return True

    def _resolve_conflict(
        self, existing: KnowledgeEntry, incoming: KnowledgeEntry,
    ) -> KnowledgeEntry:
        """Resolve a conflict between existing and incoming entries."""
        if self._conflict_strategy == ConflictStrategy.LAST_WRITE_WINS:
            incoming.citation_count = existing.citation_count
            return incoming

        if self._conflict_strategy == ConflictStrategy.HIGHEST_CITATION:
            return existing if existing.citation_count >= incoming.citation_count else incoming

        # MERGE: combine tags, keep incoming value
        merged_tags = list(set(existing.tags + incoming.tags))
        incoming.tags = merged_tags
        incoming.citation_count = max(existing.citation_count, incoming.citation_count)
        return incoming


__all__ = ["NamespaceStats", "SharedMemoryPool"]
