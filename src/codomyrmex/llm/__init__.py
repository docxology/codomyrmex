"""LLM integration modules for Codomyrmex."""

# modular Ollama implementation
from .ollama import (
    OllamaManager,
    ModelRunner,
    OutputManager,
    ConfigManager
)

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

__all__ = [
    'OllamaManager',
    'ModelRunner',
    'OutputManager',
    'ConfigManager',
    
    'LLMConfig',
    'LLMConfigPresets',
    'get_config',
    'set_config',
    'reset_config',

    'OllamaClient',
    'OllamaError',
    'OllamaConnectionError',
    'OllamaTimeoutError',
    'OllamaModelError',
]
