"""
Qwen Agent Integration

Comprehensive Qwen model integration supporting:
- DashScope API via OpenAI-compatible client (QwenClient)
- Native qwen-agent framework (Assistant, WebUI, MCP)
- 14 model variants (Qwen3-Max, Qwen-Coder, Qwen-VL, etc.)
- Tool/function calling with multi-turn loops
- 5 MCP tools for AI agent consumption
"""

__version__ = "1.1.4"

from .qwen_client import DEFAULT_MODEL, QWEN_MODELS, QwenClient

__all__ = [
    "DEFAULT_MODEL",
    "QWEN_MODELS",
    "QwenClient",
]


# Lazy imports for optional qwen-agent framework
def __getattr__(name: str):
    """Lazy import for qwen-agent framework wrappers."""
    _wrapper_exports = {
        "create_assistant",
        "create_codomyrmex_assistant",
        "launch_webui",
        "run_assistant",
        "stream_assistant",
    }
    if name in _wrapper_exports:
        from . import qwen_agent_wrapper

        return getattr(qwen_agent_wrapper, name)

    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
