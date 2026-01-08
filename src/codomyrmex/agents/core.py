from typing import Any, Iterator, Optional

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from codomyrmex.logging_monitoring import get_logger




























"""Core agent interfaces and base classes."""



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


@dataclass
class AgentRequest:
    """Request structure for agent operations."""

    prompt: str
    context: dict[str, Any] = None
    capabilities: list[AgentCapabilities] = None
    timeout: Optional[int] = None
    metadata: dict[str, Any] = None
    id: Optional[str] = None

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
    request_id: Optional[str] = None

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
        """
        self.config = config or {}
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def get_capabilities(self) -> list[AgentCapabilities]:
        """Get list of capabilities supported by this agent."""
        pass

    @abstractmethod
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute an agent request."""
        pass

    @abstractmethod
    def stream(self, request: AgentRequest) -> Iterator[str]:
        """Stream response from agent."""
        pass


class BaseAgent(AgentInterface):
    """Base implementation for agents with standard capability handling."""

    def __init__(
        self,
        name: str,
        capabilities: list[AgentCapabilities],
        config: Optional[dict[str, Any]] = None,
    ):
        super().__init__(config)
        self.name = name
        self.capabilities = capabilities or []

    def get_capabilities(self) -> list[AgentCapabilities]:
        return self.capabilities
    
    def get_config_value(self, key: str, default: Any = None, config: Optional[dict[str, Any]] = None) -> Any:
        """Helper to get config value from instance config or override."""
        cfg = config if config is not None else self.config
        return cfg.get(key, default)

    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Standard execute flow: validate -> execute_impl.
        """
        errors = self.validate_request(request)
        if errors:
            return AgentResponse(content="", error="; ".join(errors))
        
        return self._execute_impl(request)

    def stream(self, request: AgentRequest) -> Iterator[str]:
        """
        Standard stream flow: validate -> stream_impl.
        """
        errors = self.validate_request(request)
        if errors:
            yield f"Error: {'; '.join(errors)}"
            return
            
        yield from self._stream_impl(request)

    @abstractmethod
    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Implementation specific execution logic."""
        pass

    @abstractmethod
    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Implementation specific streaming logic."""
        pass

    def validate_request(self, request: AgentRequest) -> list[str]:
        errors = []
        if not request.prompt or not request.prompt.strip():
            errors.append("Prompt cannot be empty")
        
        # Check required capabilities
        for cap in request.capabilities:
            if cap not in self.capabilities:
                 errors.append(f"Capability {cap.value} not supported")
        
        return errors


class AgentIntegrationAdapter(ABC):
    """Base class for integrating agents with Codomyrmex modules."""

    def __init__(self, agent: AgentInterface):
        self.agent = agent
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs
    ) -> str:
        """Adapt agent for AI code editing module."""
        pass

    @abstractmethod
    def adapt_for_llm(
        self, messages: list[dict], model: str = None, **kwargs
    ) -> dict:
        """Adapt agent for LLM module."""
        pass

    @abstractmethod
    def adapt_for_code_execution(
        self, code: str, language: str = "python", **kwargs
    ) -> dict[str, Any]:
        """Adapt agent for code execution sandbox."""
        pass
