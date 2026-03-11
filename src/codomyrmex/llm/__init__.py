"""LLM integration modules for Codomyrmex.

Submodules:
    safety: Consolidated safety capabilities.
    multimodal: Consolidated multimodal capabilities.
    - ollama: Local LLM model management via Ollama
    - mlx: Native Apple Silicon LLM inference via MLX
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
import contextlib

with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus

# modular Ollama implementation
# Submodule exports

from . import (
    chains,
    cost_tracking,
    embeddings,
    guardrails,
    memory,
    mlx,
    multimodal,
    prompts,
    providers,
    rag,
    safety,
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
from .mlx import MLXConfig, MLXRunner
from .ollama import ConfigManager, ModelRunner, OllamaManager, OutputManager


def cli_commands():
    """Return CLI commands for the llm module."""

    def _show_config():
        config = get_config()
        print("LLM configuration:")
        for key, value in vars(config).items():
            print(f"  {key}: {value}")

    def _list_providers():
        submodules = [
            "providers",
            "chains",
            "memory",
            "tools",
            "guardrails",
            "streaming",
            "embeddings",
            "rag",
            "cost_tracking",
            "prompts",
            "mlx",
        ]
        print("LLM provider submodules:")
        for name in submodules:
            print(f"  {name}")

    return {
        "config": _show_config,
        "providers": _list_providers,
    }


__all__ = [
    "ConfigManager",
    "FabricConfigManager",
    "FabricManager",
    "FabricOrchestrator",
    "LLMConfig",
    "LLMConfigPresets",
    # MCP Integration
    "MCPBridge",
    "MCPPrompt",
    "MCPResource",
    # MLX Integration
    "MLXConfig",
    "MLXRunner",
    "ModelRunner",
    "OllamaManager",
    "OutputManager",
    "ask",
    "chains",
    "cli_commands",
    "convert_tool_to_mcp",
    "cost_tracking",
    "create_mcp_bridge_from_registry",
    "embeddings",
    "get_config",
    "guardrails",
    "memory",
    "mlx",
    "multimodal",
    "prompts",
    # Submodules
    "providers",
    "rag",
    "reset_config",
    "safety",
    "set_config",
    "streaming",
    "tools",
]


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
                messages=[Message(role="user", content=question)], model=model
            )
            return response.content
    except Exception as e:
        return f"Error querying LLM: {e!s}"
