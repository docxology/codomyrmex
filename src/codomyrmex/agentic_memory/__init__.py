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
]
