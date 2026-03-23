"""Abstract LLM provider base class."""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from .models import CompletionResponse, Message, ProviderConfig


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Supports context manager protocol:
        with get_provider(ProviderType.OPENAI, api_key="...") as provider:
            response = provider.complete(messages)
    """

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False

    def cleanup(self) -> None:
        self._client = None

    @abstractmethod
    def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> CompletionResponse:
        """Generate a completion from messages."""

    @abstractmethod
    def complete_stream(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> Iterator[str]:
        """Generate a streaming completion."""

    @abstractmethod
    async def complete_async(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> CompletionResponse:
        """Generate a completion asynchronously."""

    @abstractmethod
    def list_models(self) -> list[str]:
        """list available models for this provider."""

    def get_model(self, model: str | None = None) -> str:
        return model or self.config.default_model or self._default_model()

    @abstractmethod
    def _default_model(self) -> str:
        """Get the default model for this provider."""
