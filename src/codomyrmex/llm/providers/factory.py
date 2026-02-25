from .anthropic import AnthropicProvider
from .base import LLMProvider
from .models import ProviderConfig, ProviderType
from .openai import OpenAIProvider
from .openrouter import OpenRouterProvider


def get_provider(
    provider_type: ProviderType,
    config: ProviderConfig | None = None,
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


