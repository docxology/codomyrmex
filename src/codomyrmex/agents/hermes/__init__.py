"""Hermes Agent module for Codomyrmex.

Provides seamless integration with the NousResearch Hermes Agent CLI framework.
"""

from codomyrmex.agents.hermes._provider_router import (
    ContextCompressor,
    MCPBridgeManager,
    ProviderRouter,
    UserModel,
)
from codomyrmex.agents.hermes.hermes_client import (
    SESSION_METADATA_HERMES_SKILLS_KEY,
    HermesClient,
    HermesError,
    agent_context_for_hermes_skills,
    normalize_hermes_skill_names,
)
from codomyrmex.agents.hermes.session import (
    HermesSession,
    InMemorySessionStore,
    SessionStore,
    SQLiteSessionStore,
)
from codomyrmex.agents.hermes.templates import TemplateLibrary

__all__ = [
    "SESSION_METADATA_HERMES_SKILLS_KEY",
    "ContextCompressor",
    "HermesClient",
    "HermesError",
    "HermesSession",
    "InMemorySessionStore",
    "MCPBridgeManager",
    "ProviderRouter",
    "SQLiteSessionStore",
    "SessionStore",
    "TemplateLibrary",
    "UserModel",
    "agent_context_for_hermes_skills",
    "normalize_hermes_skill_names",
]
