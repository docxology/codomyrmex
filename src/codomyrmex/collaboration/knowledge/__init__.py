"""Cross-agent knowledge sharing.

Provides namespace-isolated knowledge pools with expertise-based
query routing for multi-agent collaboration.
"""

from codomyrmex.collaboration.knowledge.knowledge_router import KnowledgeRouter
from codomyrmex.collaboration.knowledge.models import (
    AccessLevel,
    ConflictStrategy,
    ExpertiseProfile,
    KnowledgeEntry,
    NamespaceACL,
    QueryResult,
)
from codomyrmex.collaboration.knowledge.shared_pool import SharedMemoryPool

__all__ = [
    "AccessLevel",
    "ConflictStrategy",
    "ExpertiseProfile",
    "KnowledgeEntry",
    "KnowledgeRouter",
    "NamespaceACL",
    "QueryResult",
    "SharedMemoryPool",
]
