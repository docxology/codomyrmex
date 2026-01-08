
class AgentIntegrationAdapter(ABC):
    """Base class for integrating agents with Codomyrmex modules."""

    def __init__(self, agent: AgentInterface):
        """Initialize the adapter with an agent instance."""
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
