"""
Agentic Memory Module

Long-term agent memory with retrieval and persistence.
"""

__version__ = "0.1.0"

from .models import Memory, MemoryImportance, MemoryType, RetrievalResult
from .stores import InMemoryStore, JSONFileStore, MemoryStore
from .memory import (
    AgentMemory,
    ConversationMemory,
    KnowledgeMemory,
    SummaryMemory,
    VectorStoreMemory,
)

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the agentic_memory module."""

    def _stats():
        """Show memory stats."""
        store = InMemoryStore()
        print(f"Memory Store Type: {store.__class__.__name__}")
        print(f"Available Memory Types: {[mt.value for mt in MemoryType]}")
        print(f"Importance Levels: {[mi.value for mi in MemoryImportance]}")

    def _search(query: str = ""):
        """Search memory with --query arg."""
        if not query:
            print("Usage: agentic_memory search --query <search_term>")
            return
        store = InMemoryStore()
        agent_mem = AgentMemory(store=store)
        results = agent_mem.search(query)
        if not results:
            print(f"No memories found for query: {query}")
        for r in results:
            print(f"  [{r.score:.2f}] {r.memory.content[:80]}")

    return {
        "stats": _stats,
        "search": _search,
    }


__all__ = [
    # Enums
    "MemoryType",
    "MemoryImportance",
    # Data classes
    "Memory",
    "RetrievalResult",
    # Stores
    "MemoryStore",
    "InMemoryStore",
    "JSONFileStore",
    # Core
    "AgentMemory",
    "ConversationMemory",
    "KnowledgeMemory",
    # Enhanced
    "VectorStoreMemory",
    "SummaryMemory",
    # CLI
    "cli_commands",
]
