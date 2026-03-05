"""Agent Brain — demonstrates codomyrmex agents and agentic memory.

Integrates with:
- codomyrmex.agents for agent registry, interfaces, and request/response
- codomyrmex.agentic_memory for persistent typed agent memory
- codomyrmex.logging_monitoring for structured logging

Example:
    >>> brain = AgentBrain()
    >>> mem = brain.remember("Python uses GIL for thread safety", "knowledge")
    >>> results = brain.recall("GIL", k=3)
    >>> print(len(results))
"""

from typing import Any

from codomyrmex.agents import (
    AgentCapabilities,
    AgentConfig,
    AgentInterface,
    AgentRegistry,
    BaseAgent,
    ClaudeClient,
    CodexClient,
    GeminiClient,
    get_config,
)
from codomyrmex.agentic_memory import (
    AgentMemory,
    InMemoryStore,
    Memory,
    MemoryImportance,
    MemoryType,
    RetrievalResult,
)
from codomyrmex.logging_monitoring import get_logger

HAS_AGENT_MODULES = True  # Exported for integration tests

logger = get_logger(__name__)


class AgentBrain:
    """Demonstrates agents + agentic_memory integration.

    Combines the codomyrmex agent registry (which agent providers are
    available) with a persistent AgentMemory store (InMemoryStore backend)
    for storing and recalling typed knowledge.

    Attributes:
        memory: AgentMemory instance backed by InMemoryStore.
        config: Agent configuration from codomyrmex.agents.

    Example:
        >>> brain = AgentBrain()
        >>> brain.remember("The quick brown fox", "knowledge")
        >>> results = brain.recall("fox", k=1)
        >>> print(results[0].memory.content)
    """

    def __init__(self) -> None:
        """Initialize AgentBrain with in-memory store."""
        store = InMemoryStore()
        self.memory = AgentMemory(store=store)
        self.config: AgentConfig = get_config()
        logger.info("AgentBrain initialized with InMemoryStore")

    @staticmethod
    def list_available_agents() -> list[str]:
        """Return list of available agent provider names.

        Checks which agent clients imported successfully from
        codomyrmex.agents (providers are None if SDK not installed).

        Returns:
            List of provider name strings (e.g. ["claude", "gemini"]).
        """
        providers = {
            "claude": ClaudeClient,
            "codex": CodexClient,
            "gemini": GeminiClient,
        }
        available = [name for name, cls in providers.items() if cls is not None]
        logger.debug(f"Available agent providers: {available}")
        return available

    def remember(
        self,
        content: str,
        memory_type: str = "knowledge",
        importance: str = "normal",
    ) -> Memory:
        """Store content in agent memory.

        Args:
            content: Text content to remember.
            memory_type: One of 'knowledge', 'episodic', 'semantic'.
            importance: One of 'low', 'normal', 'high', 'critical'.

        Returns:
            The stored Memory object.
        """
        mem_type = MemoryType(memory_type) if memory_type in [t.value for t in MemoryType] else MemoryType.KNOWLEDGE
        mem_importance = (
            MemoryImportance(importance)
            if importance in [i.value for i in MemoryImportance]
            else MemoryImportance.NORMAL
        )
        memory = self.memory.remember(
            content=content,
            memory_type=mem_type,
            importance=mem_importance,
        )
        logger.debug(f"Stored memory id={memory.id}, type={mem_type.value}")
        return memory

    def recall(self, query: str, k: int = 5) -> list[RetrievalResult]:
        """Retrieve relevant memories matching query.

        Args:
            query: Search query string.
            k: Maximum number of results to return.

        Returns:
            List of RetrievalResult objects ordered by relevance.
        """
        results = self.memory.recall(query=query, k=k)
        logger.debug(f"Recalled {len(results)} memories for query='{query}'")
        return results

    def agent_config_summary(self) -> dict[str, Any]:
        """Return a summary of current agent configuration.

        Returns:
            Dictionary with agent config fields.
        """
        summary = {
            "available_providers": self.list_available_agents(),
            "provider_count": len(self.list_available_agents()),
            "agent_interface": AgentInterface.__name__,
            "base_agent": BaseAgent.__name__,
            "capabilities": [cap.value for cap in AgentCapabilities],
            "registry_type": AgentRegistry.__name__ if AgentRegistry else "unavailable",
        }
        return summary
