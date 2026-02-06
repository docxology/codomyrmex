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
# Submodule exports
from . import (
    chains,
    cost_tracking,
    embeddings,
    guardrails,
    memory,
    prompts,
    providers,
    rag,
    streaming,
    tools,
)
from .config import (
    LLMConfig,
    LLMConfigPresets,
    get_config,
    reset_config,
    set_config,
)

# Fabric integration
from .fabric import FabricConfigManager, FabricManager, FabricOrchestrator

# MCP integration
from .mcp import (
    MCPBridge,
    MCPPrompt,
    MCPResource,
    convert_tool_to_mcp,
    create_mcp_bridge_from_registry,
)
from .ollama import ConfigManager, ModelRunner, OllamaManager, OutputManager

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

    # MCP Integration
    'MCPBridge',
    'MCPResource',
    'MCPPrompt',
    'convert_tool_to_mcp',
    'create_mcp_bridge_from_registry',

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

