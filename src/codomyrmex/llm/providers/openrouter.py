from collections.abc import Iterator

from .base import LLMProvider
from .models import CompletionResponse, Message, ProviderConfig, ProviderType


class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider for multi-model access.

    OpenRouter provides access to multiple LLM providers through a unified
    OpenAI-compatible API. Includes free tier models for development and testing.

    Environment variable: OPENROUTER_API_KEY

    Example:
        provider = get_provider(
            ProviderType.OPENROUTER,
            api_key=os.environ["OPENROUTER_API_KEY"]
        )
        response = provider.complete(
            messages=[Message(role="user", content="Hello")],
            model="openrouter/free"
        )
    """

    provider_type = ProviderType.OPENROUTER
    BASE_URL = "https://openrouter.ai/api/v1"

    # Free models available on OpenRouter (verified Feb 2026)
    # See https://openrouter.ai/api/v1/models for current availability
    # Use provider.list_models() to get full list from API
    FREE_MODELS = [
        "openrouter/free",  # Auto-selects best available free model
        # Meta Llama
        "meta-llama/llama-3.3-70b-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        # Google Gemma
        "google/gemma-3-27b-it:free",
        "google/gemma-3-12b-it:free",
        # Mistral
        "mistralai/mistral-small-3.1-24b-instruct:free",
        # DeepSeek
        "deepseek/deepseek-r1-0528:free",
        # NVIDIA
        "nvidia/nemotron-nano-9b-v2:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        # Other providers
        "arcee-ai/trinity-large-preview:free",
        "liquid/lfm-2.5-1.2b-instruct:free",
        "nousresearch/hermes-3-llama-3.1-405b:free",
    ]

    def __init__(self, config: ProviderConfig):
        """Execute   Init   operations natively."""
        super().__init__(config)
        # Set OpenRouter base URL if not specified
        if not self.config.base_url:
            self.config.base_url = self.BASE_URL
        # Add required OpenRouter headers
        self.config.extra_headers.update({
            "HTTP-Referer": "https://github.com/codomyrmex",
            "X-Title": "Codomyrmex",
        })
        self._init_client()

    def _init_client(self):
        """Initialize the OpenAI-compatible client for OpenRouter."""
        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
                default_headers=self.config.extra_headers,
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
        """Execute Complete operations natively."""
        if not self._client:
            raise RuntimeError("OpenRouter client not initialized. Install openai package.")

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
        """Execute Complete Stream operations natively."""
        if not self._client:
            raise RuntimeError("OpenRouter client not initialized.")

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
                default_headers=self.config.extra_headers,
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
            raise RuntimeError("OpenRouter async client not available. Install openai package.") from e

    def list_models(self) -> list[str]:
        """List free models available on OpenRouter.

        For a full list of models, see: https://openrouter.ai/models
        """
        return self.FREE_MODELS

    def _default_model(self) -> str:
        """Execute  Default Model operations natively."""
        return "openrouter/free"


