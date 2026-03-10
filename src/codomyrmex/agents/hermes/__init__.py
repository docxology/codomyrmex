"""Hermes Agent module for Codomyrmex.

Provides seamless integration with the NousResearch Hermes Agent CLI framework.
"""

from codomyrmex.agents.hermes.hermes_client import HermesClient, HermesError
from codomyrmex.agents.hermes.session import (
    HermesSession,
    InMemorySessionStore,
    SessionStore,
    SQLiteSessionStore,
)
from codomyrmex.agents.hermes.templates import TemplateLibrary

__all__ = [
    "HermesClient",
    "HermesError",
    "HermesSession",
    "InMemorySessionStore",
    "SQLiteSessionStore",
    "SessionStore",
    "TemplateLibrary",
]

