"""
LLM Provider abstractions for unified API access.

Provides a common interface for interacting with different LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Iterator, AsyncIterator
from enum import Enum
import json


class ProviderType(Enum):
    """Supported LLM providers.

    Implemented:
        OPENAI - OpenAI API (GPT models)
        ANTHROPIC - Anthropic API (Claude models)
        OPENROUTER - OpenRouter API (multi-model access, includes free models)

    Planned:
        GOOGLE - Google AI (Gemini models)
        OLLAMA - Local Ollama server
        AZURE_OPENAI - Azure OpenAI Service
        COHERE - Cohere API
        MISTRAL - Mistral AI API
    """
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    GOOGLE = "google"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"
    COHERE = "cohere"
    MISTRAL = "mistral"


@dataclass
class Message:
    """A chat message."""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class CompletionResponse:
    """Response from a completion request."""
    content: str
    model: str
    provider: ProviderType
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    tool_calls: Optional[List[Dict]] = None
    raw_response: Optional[Any] = None
    
    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        if self.usage:
            return self.usage.get("total_tokens", 0)
        return 0


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    organization: Optional[str] = None
    timeout: float = 60.0
    max_retries: int = 3
    default_model: Optional[str] = None
    extra_headers: Dict[str, str] = field(default_factory=dict)


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
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
        """Generate a completion from messages."""
        pass
    
    @abstractmethod
    def complete_stream(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """Generate a streaming completion."""
        pass
    
    @abstractmethod
    async def complete_async(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
        """Generate a completion asynchronously."""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models for this provider."""
        pass
    
    def get_model(self, model: Optional[str] = None) -> str:
        """Get model name, using default if not specified."""
        return model or self.config.default_model or self._default_model()
    
    @abstractmethod
    def _default_model(self) -> str:
        """Get the default model for this provider."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    provider_type = ProviderType.OPENAI
    
    def __init__(self, config: ProviderConfig):
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
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
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
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
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
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
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
        except ImportError:
            raise RuntimeError("OpenAI async client not available.")
    
    def list_models(self) -> List[str]:
        if not self._client:
            return []
        models = self._client.models.list()
        return [m.id for m in models.data if "gpt" in m.id.lower()]
    
    def _default_model(self) -> str:
        return "gpt-4o"


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    provider_type = ProviderType.ANTHROPIC
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._init_client()
    
    def _init_client(self):
        try:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self.config.api_key)
        except ImportError:
            self._client = None
    
    def complete(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
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
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
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
            for text in stream.text_stream:
                yield text
    
    async def complete_async(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
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
        except ImportError:
            raise RuntimeError("Anthropic async client not available.")
    
    def list_models(self) -> List[str]:
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]
    
    def _default_model(self) -> str:
        return "claude-3-5-sonnet-20241022"


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

    # Free models available on OpenRouter (as of 2026)
    # See https://openrouter.ai/api/v1/models for current availability
    FREE_MODELS = [
        "openrouter/free",  # Auto-selects best available free model
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "nvidia/nemotron-nano-12b-v2-vl:free",
        "liquid/lfm-2.5-1.2b-instruct:free",
        "arcee-ai/trinity-mini:free",
    ]

    def __init__(self, config: ProviderConfig):
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
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
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
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
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
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
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
        except ImportError:
            raise RuntimeError("OpenRouter async client not available. Install openai package.")

    def list_models(self) -> List[str]:
        """List free models available on OpenRouter.

        For a full list of models, see: https://openrouter.ai/models
        """
        return self.FREE_MODELS

    def _default_model(self) -> str:
        return "openrouter/free"


def get_provider(
    provider_type: ProviderType,
    config: Optional[ProviderConfig] = None,
    **kwargs
) -> LLMProvider:
    """Get an LLM provider instance."""
    if config is None:
        config = ProviderConfig(**kwargs)
    
    providers = {
        ProviderType.OPENAI: OpenAIProvider,
        ProviderType.ANTHROPIC: AnthropicProvider,
        ProviderType.OPENROUTER: OpenRouterProvider,
    }
    
    provider_class = providers.get(provider_type)
    if not provider_class:
        raise ValueError(f"Unsupported provider: {provider_type}")
    
    return provider_class(config)


__all__ = [
    "ProviderType",
    "Message",
    "CompletionResponse",
    "ProviderConfig",
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OpenRouterProvider",
    "get_provider",
]
