"""Language models module for local LLM integration."""

from .config import (
    LLMConfig,
    LLMConfigPresets,
    get_config,
    set_config,
    reset_config,
)
from .ollama_client import (
    OllamaClient,
    OllamaError,
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaModelError,
)
from .ollama_integration import (
    OllamaManager,
    generate_with_ollama,
    stream_with_ollama,
    chat_with_ollama,
    stream_chat_with_ollama,
    check_ollama_availability,
    get_available_models,
    create_chat_messages,
    get_default_manager,
)

__all__ = [
    # Configuration
    'LLMConfig',
    'LLMConfigPresets',
    'get_config',
    'set_config',
    'reset_config',

    # Client classes and exceptions
    'OllamaClient',
    'OllamaError',
    'OllamaConnectionError',
    'OllamaTimeoutError',
    'OllamaModelError',

    # Manager and utilities
    'OllamaManager',
    'generate_with_ollama',
    'stream_with_ollama',
    'chat_with_ollama',
    'stream_chat_with_ollama',
    'check_ollama_availability',
    'get_available_models',
    'create_chat_messages',
    'get_default_manager',
]
