"""Agent History — conversation and context persistence for agent sessions."""

__version__ = "0.1.0"

from codomyrmex.agents.history.manager import ConversationManager
from codomyrmex.agents.history.models import Conversation, HistoryMessage, MessageRole
from codomyrmex.agents.history.stores import (
    FileHistoryStore,
    InMemoryHistoryStore,
    SQLiteHistoryStore,
)

__all__ = [
    "Conversation",
    "ConversationManager",
    "FileHistoryStore",
    "HistoryMessage",
    "InMemoryHistoryStore",
    "MessageRole",
    "SQLiteHistoryStore",
]
