"""Cross-agent knowledge sharing models.

Data classes for knowledge entries, expertise profiles, and
query results used by the shared memory pool and router.
"""

from __future__ import annotations

from codomyrmex.agents.memory.store import MemoryEntry

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AccessLevel(Enum):
    """ACL permission levels for a namespace."""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class ConflictStrategy(Enum):
    """Strategy for resolving conflicting entries."""

    LAST_WRITE_WINS = "last_write_wins"
    HIGHEST_CITATION = "highest_citation"
    MERGE = "merge"


@dataclass
class KnowledgeEntry:
    """A knowledge item contributed by an agent.

    Extends the MemoryEntry concept with agent provenance,
    domain classification, and citation tracking.

    Attributes:
        key: Unique knowledge identifier.
        value: The knowledge content (text, dict, etc.).
        source_agent: ID of the agent that contributed this.
        domain: Knowledge domain (e.g. "testing", "deployment").
        tags: Searchable tags.
        citation_count: How many times other agents referenced this.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        metadata: Additional context.
    """

    key: str
    value: Any
    source_agent: str
    domain: str = ""
    tags: list[str] = field(default_factory=list)
    citation_count: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def cite(self) -> None:
        """Increment the citation count."""
        self.citation_count += 1

    def update(self, value: Any) -> None:
        """Update the value and timestamp."""
        self.value = value
        self.updated_at = time.time()


@dataclass
class ExpertiseProfile:
    """Expertise profile for an agent.

    Attributes:
        agent_id: Agent identifier.
        domains: Domains of expertise with confidence scores.
        tags: Tags this agent is knowledgeable about.
        contribution_count: Number of knowledge entries contributed.
        last_active: Timestamp of last contribution.
    """

    agent_id: str
    domains: dict[str, float] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    contribution_count: int = 0
    last_active: float = field(default_factory=time.time)


@dataclass
class QueryResult:
    """Result of a knowledge query.

    Attributes:
        query: The original query text.
        entries: Matching knowledge entries.
        routed_to: Agent ID the query was routed to (if any).
        confidence: Routing confidence score.
        search_time_ms: Time to execute the search.
    """

    query: str
    entries: list[KnowledgeEntry] = field(default_factory=list)
    routed_to: str = ""
    confidence: float = 0.0
    search_time_ms: float = 0.0


@dataclass
class NamespaceACL:
    """Access control for a namespace.

    Attributes:
        owner: Agent ID that owns the namespace.
        permissions: Mapping of agent_id → AccessLevel.
    """

    owner: str
    permissions: dict[str, AccessLevel] = field(default_factory=dict)

    def can_read(self, agent_id: str) -> bool:
        """Check if an agent has read access."""
        if agent_id == self.owner:
            return True
        perm = self.permissions.get(agent_id)
        return perm is not None

    def can_write(self, agent_id: str) -> bool:
        """Check if an agent has write access."""
        if agent_id == self.owner:
            return True
        perm = self.permissions.get(agent_id)
        return perm in (AccessLevel.WRITE, AccessLevel.ADMIN)


__all__ = [
    "AccessLevel",
    "ConflictStrategy",
    "ExpertiseProfile",
    "KnowledgeEntry",
    "NamespaceACL",
    "QueryResult",
]
