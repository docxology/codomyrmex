"""Core agent interfaces and base classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterator, Optional

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


@dataclass
class AgentRequest:
    """Request structure for agent operations."""

    prompt: str
    context: dict[str, Any] = None
    capabilities: list[AgentCapabilities] = None
    timeout: Optional[int] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.context is None:
            self.context = {}
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AgentResponse:
    """Response structure from agent operations."""

    content: str
    metadata: dict[str, Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}

    def is_success(self) -> bool:
        """Check if the response is successful."""
        return self.error is None


class AgentInterface(ABC):
    """Abstract base class for all agent implementations."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize agent.

        Args:
            config: Agent-specific configuration
        """
        self.config = config or {}
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def get_capabilities(self) -> list[AgentCapabilities]:
        """Get list of capabilities supported by this agent."""
        pass

    @abstractmethod
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute an agent request.

        Args:
            request: Agent request with prompt and context

        Returns:
            Agent response with content and metadata
        """
        pass

    @abstractmethod
    def stream(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream response from agent.

        Args:
            request: Agent request with prompt and context

        Yields:
            Chunks of response content
        """
        pass

    def supports_capability(self, capability: AgentCapabilities) -> bool:
        """Check if agent supports a specific capability."""
        return capability in self.get_capabilities()

    def validate_request(self, request: AgentRequest) -> list[str]:
        """
        Validate an agent request.

        Args:
            request: Agent request to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not request.prompt or not request.prompt.strip():
            errors.append("Prompt cannot be empty")

        # Check if requested capabilities are supported
        for capability in request.capabilities:
            if not self.supports_capability(capability):
                errors.append(
                    f"Agent does not support capability: {capability.value}"
                )

        return errors


class AgentIntegrationAdapter(ABC):
    """Base class for integrating agents with Codomyrmex modules."""

    def __init__(self, agent: AgentInterface):
        """
        Initialize integration adapter.

        Args:
            agent: Agent instance to adapt
        """
        self.agent = agent
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs
    ) -> str:
        """
        Adapt agent for AI code editing module.

        Args:
            prompt: Code generation prompt
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Generated code
        """
        pass

    @abstractmethod
    def adapt_for_llm(
        self, messages: list[dict], model: str = None, **kwargs
    ) -> dict:
        """
        Adapt agent for LLM module.

        Args:
            messages: Conversation messages
            model: Model name (optional, uses agent default)
            **kwargs: Additional parameters

        Returns:
            Completion result dictionary
        """
        pass

    @abstractmethod
    def adapt_for_code_execution(
        self, code: str, language: str = "python", **kwargs
    ) -> dict[str, Any]:
        """
        Adapt agent for code execution sandbox.

        Args:
            code: Code to execute
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Execution result dictionary
        """
        pass

