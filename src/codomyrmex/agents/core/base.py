"""Core agent interfaces and base classes."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class AgentCapabilities(Enum):
    """Capabilities that agents can support."""

    CODE_GENERATION = "code_generation"
    CODE_EDITING = "code_editing"
    CODE_ANALYSIS = "code_analysis"
    TEXT_COMPLETION = "text_completion"
    STREAMING = "streaming"
    MULTI_TURN = "multi_turn"
    CODE_EXECUTION = "code_execution"
    VISION = "vision"
    TOOL_USE = "tool_use"
    EXTENDED_THINKING = "extended_thinking"
    FILE_OPERATIONS = "file_operations"
    CACHING = "caching"
    BATCH = "batch"
    CLOUD_INFRASTRUCTURE = "cloud_infrastructure"
    CLOUD_STORAGE = "cloud_storage"
    TASK_DECOMPOSITION = "task_decomposition"


@dataclass
class AgentRequest:
    """Request structure for agent operations."""

    prompt: str
    context: dict[str, Any] | None = None
    capabilities: list[AgentCapabilities] | None = None
    timeout: int | None = None
    metadata: dict[str, Any] | None = None
    id: str | None = None
    trace_id: str | None = None

    def __post_init__(self) -> None:
        """set default optional fields to empty collections."""
        import uuid

        if self.context is None:
            self.context = {}
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}
        if self.trace_id is None:
            self.trace_id = str(uuid.uuid4())


@dataclass
class AgentResponse:
    """Response structure from agent operations."""

    content: str
    metadata: dict[str, Any] | None = None
    error: str | None = None
    execution_time: float | None = None
    tokens_used: int | None = None
    cost: float | None = None
    request_id: str | None = None
    trace_id: str | None = None

    def __post_init__(self) -> None:
        """set default optional fields to empty collections."""
        if self.metadata is None:
            self.metadata = {}

    def is_success(self) -> bool:
        """Check if the response is successful."""
        return self.error is None


class AgentInterface(ABC):
    """Abstract base class for all agent implementations."""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize agent.
        """
        self.config = config or {}
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def get_capabilities(self) -> list[AgentCapabilities]:
        """Get list of capabilities supported by this agent."""

    @abstractmethod
    def execute(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        """Execute an agent request."""

    @abstractmethod
    def stream(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream agent response.

        Args:
            request: Agent request

        Yields:
            Response chunks
        """

    @abstractmethod
    def setup(self) -> None:
        """
        Interactive setup for the agent.

        This method should guide the user through the configuration process,
        checking for necessary environment variables, API keys, and other
        requirements.
        """

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connection to the underlying service.

        Returns:
            True if connection is successful, False otherwise
        """

    @abstractmethod
    def supports_capability(self, capability: AgentCapabilities) -> bool:
        """Check if agent supports a specific capability."""


@runtime_checkable
class AgentProtocol(Protocol):
    """Protocol defining the plan-act-observe agent lifecycle.

    Any agent that supports structured reasoning should implement
    these three methods.  ``BaseAgent`` provides default no-op
    implementations so adoption is incremental.
    """

    def plan(self, request: AgentRequest) -> list[str]:
        """Generate a plan of actions to execute.

        Args:
            request: The incoming agent request.

        Returns:
            Ordered list of action descriptions the agent intends to take.
        """
        ...

    def act(self, action: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Execute a single planned action.

        Args:
            action: The action string (e.g. tool name or reasoning step).
            context: Optional context from previous observations.

        Returns:
            Agent response from executing the action.
        """
        ...

    def observe(self, response: AgentResponse) -> dict[str, Any]:
        """Process the result of an action and extract observations.

        Args:
            response: The response from the most recent ``act()`` call.

        Returns:
            Observation dict that can feed into the next ``plan()``
            or ``act()`` call.
        """
        ...


class BaseAgent(AgentInterface):
    """Base implementation of AgentInterface with common functionality."""

    def __init__(
        self,
        name: str,
        capabilities: list[AgentCapabilities],
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize base agent.

        Args:
            name: Agent name
            capabilities: list of agent capabilities
            config: Agent configuration
        """
        super().__init__(config)
        self.name = name
        self.capabilities = capabilities or []

    # ------------------------------------------------------------------
    # AgentProtocol default implementations (plan / act / observe)
    # ------------------------------------------------------------------

    def plan(self, request: AgentRequest) -> list[str]:
        """Default plan: single step that executes the prompt directly."""
        return [request.prompt]

    def act(self, action: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Default act: wrap the action string as an AgentRequest and execute."""
        return self.execute(AgentRequest(prompt=action, context=context))

    def observe(self, response: AgentResponse) -> dict[str, Any]:
        """Default observe: return content and success status."""
        return {
            "content": response.content,
            "success": response.is_success(),
            "error": response.error,
        }

    def setup(self) -> None:
        """
        Default setup implementation.
        """
        self.logger.info("Setting up agent: %s", self.name)
        # Base implementation does nothing but log

    def test_connection(self) -> bool:
        """
        Default connection test.

        Returns:
            True (default assumption if not overridden)
        """
        self.logger.info("Testing connection for agent: %s", self.name)
        # Default to True for base agent, override in subclasses
        return True

    def execute(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        """
        Execute agent request.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        try:
            from codomyrmex.logging_monitoring.core.correlation import with_correlation

            self._validate_request(request)
            with with_correlation(request.trace_id):
                response = self._execute_impl(request, max_tokens=max_tokens)
                response.trace_id = request.trace_id
                return response
        except Exception as e:
            self.logger.exception("Error executing %s request", self.name)
            return AgentResponse(
                content="",
                error=str(e),
                metadata={"error_type": type(e).__name__},
                request_id=request.id,
            )

    def stream(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream agent response.

        Args:
            request: Agent request

        Yields:
            Response chunks
        """
        try:
            from codomyrmex.logging_monitoring.core.correlation import with_correlation

            self._validate_request(request)
            with with_correlation(request.trace_id):
                yield from self._stream_impl(request)
        except Exception as e:
            self.logger.exception("Error streaming %s response", self.name)
            yield f"Error: {e!s}"

    def _validate_request(self, request: AgentRequest) -> None:
        """
        Validate agent request.

        Args:
            request: Agent request

        Raises:
            ValueError: If request is invalid
        """
        if not request.prompt:
            raise ValueError("Prompt is required")

        # Check required capabilities if specified in request
        if request.capabilities:
            for cap in request.capabilities:
                if cap not in self.capabilities:
                    self.logger.warning(
                        "Request requires capability %s not supported by agent %s",
                        cap,
                        self.name,
                    )

    def _execute_impl(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        """
        Implementation of execute method.

        Args:
            request: Agent request

        Returns:
            Agent response

        Raises:
            NotImplementedError: If not implemented
        """
        raise NotImplementedError  # ABC: intentional

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Implementation of stream method.

        Args:
            request: Agent request

        Yields:
            Response chunks

        Raises:
            NotImplementedError: If not implemented
        """
        raise NotImplementedError  # ABC: intentional

    def get_capabilities(self) -> list[AgentCapabilities]:
        """
        Get agent capabilities.

        Returns:
            list of agent capabilities
        """
        return self.capabilities

    def supports_capability(self, capability: AgentCapabilities) -> bool:
        """
        Check if agent supports a specific capability.

        Args:
            capability: Capability to check

        Returns:
            True if supported, False otherwise
        """
        return capability in self.get_capabilities()

    def get_config_value(
        self, key: str, default: Any = None, config: dict[str, Any] | None = None
    ) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value
            config: Optional configuration override

        Returns:
            Configuration value
        """
        # Check override config first
        if config and key in config:
            return config[key]

        # Check instance config
        if self.config and key in self.config:
            return self.config[key]

        # Use imported get_config to check global config
        # Note: We import inside method to avoid circular imports if config.py imports core
        from codomyrmex.agents.core.config import get_config as get_global_config

        global_config = get_global_config()
        if hasattr(global_config, key):
            return getattr(global_config, key)

        return default


class AgentIntegrationAdapter(ABC):
    """Base class for integrating agents with Codomyrmex modules."""

    def __init__(self, agent: AgentInterface):
        """Initialize adapter."""

        self.agent = agent
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs: Any
    ) -> str:
        """Adapt agent for AI code editing module."""

    @abstractmethod
    def adapt_for_llm(
        self, messages: list[dict[str, Any]], model: str | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Adapt agent for LLM module."""

    @abstractmethod
    def adapt_for_code_execution(
        self, code: str, language: str = "python", **kwargs: Any
    ) -> dict[str, Any]:
        """Adapt agent for code execution sandbox."""
