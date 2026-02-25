"""AI Code Utilities."""

import os

try:
    from codomyrmex.llm.providers.ollama_manager import OLLAMA_AVAILABLE
except ImportError:
    OLLAMA_AVAILABLE = False

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .models import CodeLanguage

try:
    from environment_setup.env_checker import check_and_setup_env_vars
except ImportError:
    check_and_setup_env_vars = None

logger = get_logger(__name__)

def get_supported_languages() -> list[CodeLanguage]:
    """Get list of supported programming languages."""
    return list(CodeLanguage)

def get_supported_providers() -> list[str]:
    """Get list of supported LLM providers."""
    providers = ["openai", "anthropic", "google"]
    if OLLAMA_AVAILABLE:
        providers.append("ollama")
    return providers

def get_available_models(provider: str) -> list[str]:
    """Get list of available models for a provider."""
    models = {
        "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "anthropic": ["claude-instant-1", "claude-2", "claude-3-sonnet"],
        "google": ["gemini-pro", "gemini-pro-vision"],
        "ollama": ["llama3.1:latest", "llama3.1:8b", "codellama:latest", "gemma2:2b", "mistral:latest"],
    }
    return models.get(provider.lower(), [])

def validate_api_keys() -> dict[str, bool]:
    """Validate API keys for all supported providers."""
    validation_results = {}

    for provider in get_supported_providers():
        key_name = f"{provider.upper()}_API_KEY"
        validation_results[provider] = bool(os.environ.get(key_name))

    return validation_results

def setup_environment() -> bool:
    """Execute Setup Environment operations natively."""
    # Setup environment variables and check dependencies.
    try:
        # Check and setup environment variables if available
        if check_and_setup_env_vars:
            check_and_setup_env_vars()

        # Validate API keys
        api_keys = validate_api_keys()
        available_providers = [
            provider for provider, available in api_keys.items() if available
        ]

        if not available_providers:
            logger.warning("No API keys found for any LLM provider")
            return False

        logger.info(f"Available LLM providers: {', '.join(available_providers)}")
        return True

    except (OSError, ValueError, AttributeError, RuntimeError) as e:
        logger.error(f"Error setting up environment: {e}")
        return False

