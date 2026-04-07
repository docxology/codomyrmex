"""Bridges from agentic memory to external systems (Obsidian, CogniLayer)."""

from codomyrmex.agentic_memory.cognilayer_bridge import COGNILAYER_DB, COGNILAYER_HOME
from codomyrmex.agentic_memory.bridges.cognilayer_bridge import (
    consolidate_memories,
    get_memory_stats,
    recall_memory,
    store_memory,
)
from codomyrmex.agentic_memory.bridges.obsidian_bridge import ObsidianMemoryBridge

__all__ = [
    "COGNILAYER_DB",
    "COGNILAYER_HOME",
    "ObsidianMemoryBridge",
    "consolidate_memories",
    "get_memory_stats",
    "recall_memory",
    "store_memory",
]
