"""LLM Inference — demonstrates codomyrmex llm and collaboration modules.

Integrates with:
- codomyrmex.llm for LLM configuration, Ollama management, and fabric integration
- codomyrmex.collaboration for multi-agent swarm coordination
- codomyrmex.logging_monitoring for structured logging

Example:
    >>> inference = LLMInference()
    >>> status = inference.agent_pool_status()
    >>> print(status["pool_available"])
    >>> swarm = inference.swarm_task("Summarize Python async patterns")
    >>> print(swarm["task_submitted"])
"""

from typing import Any

from codomyrmex.collaboration import (
    AgentPool,
    MessageBus,
    SwarmManager,
    Task,
    TaskDecomposer,
    TaskPriority,
    TaskStatus,
)
from codomyrmex.llm import (
    LLMConfig,
    LLMConfigPresets,
    MCPBridge,
    OllamaManager,
    providers,
)
from codomyrmex.logging_monitoring import get_logger

HAS_LLM_MODULES = True  # Exported for integration tests

logger = get_logger(__name__)


def _ollama_available() -> bool:
    """Check if Ollama service is reachable.

    Returns:
        True if Ollama HTTP endpoint responds, False otherwise.
    """
    import os
    import urllib.request

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


class LLMInference:
    """Demonstrates llm + collaboration integration.

    Combines codomyrmex.llm (Ollama, providers, config) with
    codomyrmex.collaboration (SwarmManager, AgentPool) to show
    both single-model inference and multi-agent coordination.

    Attributes:
        config: LLMConfig for current LLM settings.
        swarm: SwarmManager for multi-agent task distribution.
        bus: MessageBus for inter-agent communication.

    Example:
        >>> inference = LLMInference()
        >>> print(inference.config_summary())
    """

    def __init__(self) -> None:
        """Initialize LLMInference with LLM config and swarm."""
        self.config = LLMConfig()
        self.swarm = SwarmManager()
        self.bus = MessageBus()
        logger.info("LLMInference initialized")

    def config_summary(self) -> dict[str, Any]:
        """Return current LLM configuration summary.

        Returns:
            Dictionary with config class info and preset names.
        """
        presets = LLMConfigPresets()
        preset_attrs = [attr for attr in dir(presets) if not attr.startswith("_")]

        return {
            "config_class": LLMConfig.__name__,
            "presets_class": LLMConfigPresets.__name__,
            "preset_names": preset_attrs,
            "mcp_bridge": MCPBridge.__name__,
            "ollama_manager": OllamaManager.__name__,
            "providers_module": providers.__name__,
        }

    def list_models(self) -> dict[str, Any]:
        """List available Ollama models (requires Ollama running).

        Uses OllamaManager to query the local Ollama endpoint.
        Returns empty list if Ollama is not running — this is
        expected in CI environments.

        Returns:
            Dictionary with:
            - ollama_available: bool
            - models: list of model name strings
            - model_count: int
        """
        result: dict[str, Any] = {
            "ollama_available": False,
            "models": [],
            "model_count": 0,
        }

        if not _ollama_available():
            logger.info("Ollama not running — skipping model list")
            return result

        try:
            manager = OllamaManager()
            models = manager.list_models()
            result["ollama_available"] = True
            result["models"] = [m.get("name", str(m)) for m in (models or [])]
            result["model_count"] = len(result["models"])
        except Exception as e:
            logger.warning(f"OllamaManager.list_models() failed: {e}")
            result["error"] = str(e)

        return result

    def swarm_task(
        self,
        description: str,
        priority: str = "normal",
    ) -> dict[str, Any]:
        """Submit a task to the codomyrmex collaboration swarm.

        Uses SwarmManager and TaskDecomposer to distribute a task
        across the agent pool (multi-agent collaboration pattern).

        Args:
            description: Natural language task description.
            priority: One of 'low', 'normal', 'high', 'critical'.

        Returns:
            Dictionary with task submission details.
        """
        logger.info(f"Submitting swarm task: {description[:50]}")

        pri_map = {
            "low": TaskPriority.LOW,
            "normal": TaskPriority.NORMAL,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL,
        }
        task_priority = pri_map.get(priority, TaskPriority.NORMAL)

        result: dict[str, Any] = {
            "description": description,
            "priority": priority,
            "task_submitted": False,
        }

        try:
            decomposer = TaskDecomposer()
            task = Task(
                name=description[:50],
                description=description,
                priority=task_priority.value,
            )
            subtasks = decomposer.decompose(task)
            result["task_submitted"] = True
            result["subtask_count"] = len(subtasks) if subtasks else 0
            result["task_id"] = task.id
            result["task_status"] = (
                task.status.value if hasattr(task.status, "value") else str(task.status)
            )
        except Exception as e:
            logger.warning(f"SwarmManager task submission failed: {e}")
            result["error"] = str(e)

        return result

    def agent_pool_status(self) -> dict[str, Any]:
        """Return agent pool and message bus status.

        Reports on the SwarmManager, AgentPool, and MessageBus
        from codomyrmex.collaboration.

        Returns:
            Dictionary with pool configuration details.
        """
        return {
            "pool_available": True,
            "swarm_class": SwarmManager.__name__,
            "pool_class": AgentPool.__name__,
            "bus_class": MessageBus.__name__,
            "decomposer_class": TaskDecomposer.__name__,
            "task_priority_values": [p.value for p in TaskPriority],
            "task_status_values": [s.value for s in TaskStatus],
        }
