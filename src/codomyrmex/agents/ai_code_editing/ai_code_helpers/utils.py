"""AI Code Utilities."""

import os

from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars
from codomyrmex.logging_monitoring import get_logger

from .models import CodeLanguage

logger = get_logger(__name__)


def get_supported_languages() -> list[CodeLanguage]:
    """Get list of supported programming languages."""
    return list(CodeLanguage)


def get_supported_providers() -> list[str]:
    """Get list of supported LLM providers."""
    return ["openai", "anthropic", "google", "ollama"]


def get_available_models(provider: str) -> list[str]:
    """Get list of available models for a provider."""
    models = {
        "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "anthropic": ["claude-instant-1", "claude-2", "claude-3-sonnet"],
        "google": ["gemini-pro", "gemini-pro-vision"],
        "ollama": [
            "llama3.1:latest",
            "llama3.1:8b",
            "codellama:latest",
            "gemma2:2b",
            "mistral:latest",
        ],
    }
    return models.get(provider.lower(), [])


# Providers that run without an API key (Ollama serves local models).
_KEYLESS_PROVIDERS = frozenset({"ollama"})


def validate_api_keys() -> dict[str, bool]:
    """Report whether ``<PROVIDER>_API_KEY`` is set for each key-based provider."""
    return {
        provider: bool(os.environ.get(f"{provider.upper()}_API_KEY"))
        for provider in get_supported_providers()
        if provider not in _KEYLESS_PROVIDERS
    }


def setup_environment() -> bool:
    # Setup environment variables and check dependencies.
    try:
        # Load .env and check environment variables
        check_and_setup_env_vars()

        # Validate API keys
        api_keys = validate_api_keys()
        available_providers = [
            provider for provider, available in api_keys.items() if available
        ]

        if not available_providers:
            logger.warning("No API keys found for any LLM provider")
            return False

        logger.info("Available LLM providers: %s", ", ".join(available_providers))
        return True

    except (OSError, ValueError, AttributeError, RuntimeError) as e:
        logger.error("Error setting up environment: %s", e)
        return False
