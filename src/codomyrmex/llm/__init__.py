"""LLM integration modules for Codomyrmex.

Submodules:
    - ollama: Local LLM model management via Ollama
    - fabric: Microsoft Fabric AI integration
    - providers: Multi-provider LLM client interfaces
    - chains: Multi-step reasoning chains
    - memory: Conversation and context memory
    - tools: LLM tool/function calling support
    - guardrails: Input/output safety validation
    - streaming: Streaming response handlers
    - embeddings: Text embedding generation and caching
    - rag: Retrieval-Augmented Generation pipeline
    - cost_tracking: Token counting and billing estimation
    - prompts: Prompt versioning and template management
"""

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

# Submodule exports
from . import providers
from . import chains
from . import memory
from . import tools
from . import guardrails
from . import streaming
from . import embeddings
from . import rag
from . import cost_tracking
from . import prompts

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
    'guardrails',
    'streaming',
    'embeddings',
    'rag',
    'cost_tracking',
    'prompts',
]
