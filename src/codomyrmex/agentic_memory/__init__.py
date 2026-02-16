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
    "search_memory",
    "add_memory",
]


# =============================================================================
# MCP Tools
# =============================================================================

from codomyrmex.model_context_protocol.decorators import mcp_tool
from typing import List, Dict, Any

def _get_default_memory():
    from .memory import AgentMemory
    from .stores import JSONFileStore
    from pathlib import Path
    
    # Use a persistent JSON store in the user's home directory
    store_path = Path.home() / ".codomyrmex" / "memory.json"
    store = JSONFileStore(file_path=str(store_path))
    return AgentMemory(store=store)

@mcp_tool(category="memory")
def search_memory(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search agentic long-term memory.
    
    Args:
        query: Search query string
        limit: Max number of results (default: 5)
        
    Returns:
        List of matching memory items with scores.
    """
    try:
        mem = _get_default_memory()
        results = mem.search(query, limit=limit)
        return [
            {
                "content": r.memory.content,
                "score": r.score,
                "created_at": r.memory.created_at.isoformat(),
                "metadata": r.memory.metadata
            }
            for r in results
        ]
    except Exception as e:
        return [{"error": str(e)}]

@mcp_tool(category="memory")
def add_memory(content: str, importance: int = 1, metadata: Dict[str, Any] = None) -> str:
    """
    Add a new item to long-term agentic memory.
    
    Args:
        content: The text content to remember
        importance: 1-10 importance score (default: 1)
        metadata: Optional dictionary of metadata
        
    Returns:
        Status message.
    """
    try:
        mem = _get_default_memory()
        from .models import MemoryImportance
        
        # Map integer to enum (roughly)
        imp_enum = MemoryImportance.LOW
        if importance >= 8:
            imp_enum = MemoryImportance.CRITICAL
        elif importance >= 5:
            imp_enum = MemoryImportance.HIGH
        elif importance >= 3:
            imp_enum = MemoryImportance.MEDIUM
            
        mem.add(content=content, importance=imp_enum, metadata=metadata or {})
        return "Memory added successfully."
    except Exception as e:
        return f"Error adding memory: {str(e)}"
