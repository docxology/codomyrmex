"""Language models module for local LLM integration."""

from .config import (
    LLMConfig,
    LLMConfigPresets,
    get_config,
    reset_config,
    set_config,
)
from .ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaError,
    OllamaModelError,
    OllamaTimeoutError,
)
from .ollama_integration import (
    OllamaManager,
    chat_with_ollama,
    check_ollama_availability,
    create_chat_messages,
    generate_with_ollama,
    get_available_models,
    get_default_manager,
    stream_chat_with_ollama,
    stream_with_ollama,
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
