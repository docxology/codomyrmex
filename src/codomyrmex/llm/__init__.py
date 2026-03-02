"""LLM integration modules for Codomyrmex.

Submodules:
    safety: Consolidated safety capabilities.
    multimodal: Consolidated multimodal capabilities.
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

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

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


def cli_commands():
    """Return CLI commands for the llm module."""
    def _show_config():
        """show Config ."""
        config = get_config()
        print("LLM configuration:")
        for key, value in vars(config).items():
            print(f"  {key}: {value}")

    def _list_providers():
        """list Providers ."""
        submodules = [
            "providers", "chains", "memory", "tools",
            "guardrails", "streaming", "embeddings",
            "rag", "cost_tracking", "prompts",
        ]
        print("LLM provider submodules:")
        for name in submodules:
            print(f"  {name}")

    return {
        "config": _show_config,
        "providers": _list_providers,
    }


from . import multimodal, safety

__all__ = [
    "safety",
    "multimodal",
    'cli_commands',
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
    'ask',
]


# =============================================================================
# MCP Tools
# =============================================================================

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="llm")
def ask(question: str, model: str = "openrouter/free") -> str:
    """
    Ask a question to an LLM provider (default: OpenRouter Free Tier).

    Args:
        question: The prompt/question to ask
        model: Model to use (default: openrouter/free)

    Returns:
        The text response from the LLM.
    """
    import os

    from .providers import Message, ProviderConfig, ProviderType, get_provider

    # Use OpenRouter by default as it has free models
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: OPENROUTER_API_KEY not set in environment."

    try:
        config = ProviderConfig(api_key=api_key)
        with get_provider(ProviderType.OPENROUTER, config) as provider:
            response = provider.complete(
                messages=[Message(role="user", content=question)],
                model=model
            )
            return response.content
    except Exception as e:
        return f"Error querying LLM: {str(e)}"

