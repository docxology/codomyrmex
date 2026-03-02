from collections.abc import Iterator

from .base import LLMProvider
from .models import CompletionResponse, Message, ProviderConfig, ProviderType


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    provider_type = ProviderType.OPENAI

    def __init__(self, config: ProviderConfig):
        """Initialize this instance."""
        super().__init__(config)
        self._init_client()

    def _init_client(self):
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                organization=self.config.organization,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
            )
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
            raise RuntimeError("OpenAI client not initialized. Install openai package.")

        response = self._client.chat.completions.create(
            model=self.get_model(model),
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        choice = response.choices[0]
        return CompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            provider=self.provider_type,
            finish_reason=choice.finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            } if response.usage else None,
            tool_calls=[tc.model_dump() for tc in choice.message.tool_calls] if choice.message.tool_calls else None,
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
            raise RuntimeError("OpenAI client not initialized.")

        stream = self._client.chat.completions.create(
            model=self.get_model(model),
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def complete_async(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> CompletionResponse:
        try:
            from openai import AsyncOpenAI
            async_client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )
            response = await async_client.chat.completions.create(
                model=self.get_model(model),
                messages=[m.to_dict() for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            choice = response.choices[0]
            return CompletionResponse(
                content=choice.message.content or "",
                model=response.model,
                provider=self.provider_type,
                finish_reason=choice.finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                } if response.usage else None,
                tool_calls=[tc.model_dump() for tc in choice.message.tool_calls] if choice.message.tool_calls else None,
                raw_response=response,
            )
        except ImportError as e:
            raise RuntimeError("OpenAI async client not available.") from e

    def list_models(self) -> list[str]:
        """list Models ."""
        if not self._client:
            return []
        models = self._client.models.list()
        return [m.id for m in models.data if "gpt" in m.id.lower()]

    def _default_model(self) -> str:
        """default Model ."""
        return "gpt-4o"


