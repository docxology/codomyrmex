"""Agentic Memory — persistent, searchable agent memory with typed retrieval.

Provides Memory models, in-memory and file-backed stores, agent-level
search/recall, Obsidian vault integration, and a rules submodule exposing
the hierarchical .cursorrules coding governance system via Python API and
MCP tools.
"""

from importlib import import_module

# Keep package import lightweight.  ``core.memory`` optionally imports the
# sentence-transformers/torch stack, so eager exports made MCP discovery load
# heavyweight native extensions merely to inspect ``mcp_tools`` metadata.
# Public imports remain source-compatible through PEP 562 lazy resolution.
_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "AgentMemory": (".core.memory", "AgentMemory"),
    "ConversationMemory": (".core.memory", "ConversationMemory"),
    "KnowledgeMemory": (".core.memory", "KnowledgeMemory"),
    "VectorStoreMemory": (".core.memory", "VectorStoreMemory"),
    "Memory": (".core.models", "Memory"),
    "MemoryImportance": (".core.models", "MemoryImportance"),
    "MemoryType": (".core.models", "MemoryType"),
    "RetrievalResult": (".core.models", "RetrievalResult"),
    "KnowledgeItemIndex": (".ki_index", "KnowledgeItemIndex"),
    "ObsidianMemoryBridge": (".obsidian_bridge", "ObsidianMemoryBridge"),
    "Rule": (".rules", "Rule"),
    "RuleEngine": (".rules", "RuleEngine"),
    "RuleLoader": (".rules", "RuleLoader"),
    "RulePriority": (".rules", "RulePriority"),
    "RuleRegistry": (".rules", "RuleRegistry"),
    "RuleSection": (".rules", "RuleSection"),
    "RuleSet": (".rules", "RuleSet"),
    "SQLiteStore": (".sqlite_store", "SQLiteStore"),
    "InMemoryStore": (".stores", "InMemoryStore"),
    "JSONFileStore": (".stores", "JSONFileStore"),
    "UserProfile": (".user_profile", "UserProfile"),
}


def __getattr__(name: str):
    """Resolve public memory classes only when callers explicitly request them."""
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = target
    value = getattr(import_module(module_name, __name__), attribute)
    globals()[name] = value
    return value


__all__ = [
    "AgentMemory",
    "ConversationMemory",
    "InMemoryStore",
    "JSONFileStore",
    "KnowledgeItemIndex",
    "KnowledgeMemory",
    "Memory",
    "MemoryImportance",
    "MemoryType",
    "ObsidianMemoryBridge",
    "RetrievalResult",
    "Rule",
    "RuleEngine",
    "RuleLoader",
    "RulePriority",
    "RuleRegistry",
    "RuleSection",
    "RuleSet",
    "SQLiteStore",
    "UserProfile",
    "VectorStoreMemory",
]
