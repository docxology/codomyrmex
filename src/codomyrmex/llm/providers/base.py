from abc import ABC, abstractmethod
from collections.abc import Iterator

from .models import CompletionResponse, Message, ProviderConfig, ProviderType


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Supports context manager protocol for clean resource management:

        with get_provider(ProviderType.OPENAI, api_key="...") as provider:
            response = provider.complete(messages)
    """

    provider_type: ProviderType

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._client = None

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and cleanup resources."""
        self.cleanup()
        return False

    def cleanup(self):
        """Clean up provider resources. Override in subclasses if needed."""
        self._client = None

    @abstractmethod
    def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> CompletionResponse:
        """Generate a completion from messages."""
        pass

    @abstractmethod
    def complete_stream(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> Iterator[str]:
        """Generate a streaming completion."""
        pass

    @abstractmethod
    async def complete_async(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> CompletionResponse:
        """Generate a completion asynchronously."""
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        """List available models for this provider."""
        pass

    def get_model(self, model: str | None = None) -> str:
        """Get model name, using default if not specified."""
        return model or self.config.default_model or self._default_model()

    @abstractmethod
    def _default_model(self) -> str:
        """Get the default model for this provider."""
        pass


