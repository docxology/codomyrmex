"""
LLM Provider abstractions for unified API access.

Provides a common interface for interacting with different LLM providers.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


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
    name: str | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
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
    finish_reason: str | None = None
    usage: dict[str, int] | None = None
    tool_calls: list[dict] | None = None
    raw_response: Any | None = None

    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        if self.usage:
            return self.usage.get("total_tokens", 0)
        return 0


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    api_key: str | None = None
    base_url: str | None = None
    organization: str | None = None
    timeout: float = 60.0
    max_retries: int = 3
    default_model: str | None = None
    extra_headers: dict[str, str] = field(default_factory=dict)


