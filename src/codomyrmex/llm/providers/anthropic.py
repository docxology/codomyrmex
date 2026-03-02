from collections.abc import Iterator

from .base import LLMProvider
from .models import CompletionResponse, Message, ProviderConfig, ProviderType


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    provider_type = ProviderType.ANTHROPIC

    def __init__(self, config: ProviderConfig):
        """Initialize this instance."""
        super().__init__(config)
        self._init_client()

    def _init_client(self):
        """init Client ."""
        try:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self.config.api_key)
        except ImportError:
            self._client = None

    def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> CompletionResponse:
        """complete ."""
        if not self._client:
            raise RuntimeError("Anthropic client not initialized.")

        # Extract system message
        system = None
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        response = self._client.messages.create(
            model=self.get_model(model),
            messages=chat_messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            **kwargs
        )

        return CompletionResponse(
            content=response.content[0].text if response.content else "",
            model=response.model,
            provider=self.provider_type,
            finish_reason=response.stop_reason,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            raw_response=response,
        )

    def complete_stream(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> Iterator[str]:
        """complete Stream ."""
        if not self._client:
            raise RuntimeError("Anthropic client not initialized.")

        system = None
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        with self._client.messages.stream(
            model=self.get_model(model),
            messages=chat_messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            **kwargs
        ) as stream:
            yield from stream.text_stream

    async def complete_async(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> CompletionResponse:
        try:
            from anthropic import AsyncAnthropic
            async_client = AsyncAnthropic(api_key=self.config.api_key)

            system = None
            chat_messages = []
            for m in messages:
                if m.role == "system":
                    system = m.content
                else:
                    chat_messages.append({"role": m.role, "content": m.content})

            response = await async_client.messages.create(
                model=self.get_model(model),
                messages=chat_messages,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens or 4096,
                **kwargs
            )

            return CompletionResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                provider=self.provider_type,
                finish_reason=response.stop_reason,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                } if response.usage else None,
                raw_response=response,
            )
        except ImportError as e:
            raise RuntimeError("Anthropic async client not available.") from e

    def list_models(self) -> list[str]:
        """list Models ."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

    def _default_model(self) -> str:
        """default Model ."""
        return "claude-3-5-sonnet-20241022"


