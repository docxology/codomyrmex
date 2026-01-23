"""LLM integration modules for Codomyrmex."""

# modular Ollama implementation
from .ollama import (
    OllamaManager,
    ModelRunner,
    OutputManager,
    ConfigManager
)

# Fabric integration
from .fabric import (
    FabricManager,
    FabricOrchestrator,
    FabricConfigManager
)

from .config import (
    LLMConfig,
    LLMConfigPresets,
    get_config,
    reset_config,
    set_config,
)

# New submodule exports
from . import providers
from . import chains
from . import memory
from . import tools

__all__ = [
    'OllamaManager',
    'ModelRunner',
    'OutputManager',
    'ConfigManager',
    
    'FabricManager',
    'FabricOrchestrator',
    'FabricConfigManager',
    
    'LLMConfig',
    'LLMConfigPresets',
    'get_config',
    'set_config',
    'reset_config',
    
    # Submodules
    'providers',
    'chains',
    'memory',
    'tools',
]

