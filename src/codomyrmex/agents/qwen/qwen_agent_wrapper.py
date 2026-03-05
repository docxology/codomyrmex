"""Qwen-Agent framework wrapper for Codomyrmex.

Provides a high-level interface to the `qwen-agent` library, which supports:
- Assistant agents with function/tool calling
- Native MCP server integration
- Built-in tools (code interpreter, image generation, web search)
- Multi-agent orchestration
- WebUI for interactive chat
"""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

try:
    from qwen_agent.agents import Assistant
except ImportError:
    Assistant = None

try:
    from qwen_agent.gui import WebUI
except ImportError:
    WebUI = None

try:
    from qwen_agent.utils.output_beautify import typewriter_print
except ImportError:
    typewriter_print = None


# --- Built-in tools ---

QWEN_BUILTIN_TOOLS: list[str] = [
    "code_interpreter",
    "image_gen",
    "amap_weather",
]


def create_assistant(
    *,
    model: str = "qwen3-max",
    model_type: str = "qwen_dashscope",
    name: str = "Codomyrmex Qwen Assistant",
    description: str = "An AI assistant powered by Qwen, integrated with Codomyrmex tools.",
    tools: list[Any] | None = None,
    mcp_servers: dict[str, dict[str, Any]] | None = None,
    system_message: str = "",
    api_key: str | None = None,
) -> Any:
    """Create a Qwen-Agent Assistant with optional MCP server integration.

    Args:
        model: Qwen model name (e.g., 'qwen3-max', 'qwen-coder-turbo').
        model_type: Model backend type ('qwen_dashscope' or 'oai').
        name: Assistant display name.
        description: Assistant description.
        tools: List of tool specs (strings for built-ins, dicts for custom).
        mcp_servers: Dict of MCP server configs for native MCP integration.
            Example: {'time': {'command': 'uvx', 'args': ['mcp-server-time']}}
        system_message: System prompt for the assistant.
        api_key: Explicit API key (default: reads DASHSCOPE_API_KEY env).

    Returns:
        qwen_agent.agents.Assistant instance.

    Raises:
        ImportError: If qwen-agent is not installed.
    """
    if Assistant is None:
        msg = (
            "qwen-agent is not installed. "
            "Install with: uv pip install qwen-agent"
        )
        raise ImportError(msg)

    llm_cfg: dict[str, Any] = {
        "model": model,
        "model_type": model_type,
    }
    if api_key:
        llm_cfg["api_key"] = api_key

    function_list: list[Any] = []
    if tools:
        function_list.extend(tools)
    if mcp_servers:
        function_list.append({"mcpServers": mcp_servers})

    return Assistant(
        llm=llm_cfg,
        function_list=function_list or None,
        name=name,
        description=description,
        system_message=system_message,
    )


def run_assistant(
    assistant: Any,
    query: str,
    *,
    history: list[dict[str, str]] | None = None,
) -> str:
    """Run a single query through a Qwen-Agent Assistant.

    Args:
        assistant: A qwen_agent.agents.Assistant instance.
        query: User query string.
        history: Optional prior conversation messages.

    Returns:
        Full response text.
    """
    messages = list(history or [])
    messages.append({"role": "user", "content": query})

    response_text = ""
    for response in assistant.run(messages=messages):
        # response is a list of message dicts
        if isinstance(response, list) and response:
            last = response[-1]
            if isinstance(last, dict) and "content" in last:
                response_text = last["content"]

    return response_text


def stream_assistant(
    assistant: Any,
    query: str,
    *,
    history: list[dict[str, str]] | None = None,
):
    """Stream responses from a Qwen-Agent Assistant.

    Args:
        assistant: A qwen_agent.agents.Assistant instance.
        query: User query string.
        history: Optional prior conversation messages.

    Yields:
        Incremental response text.
    """
    messages = list(history or [])
    messages.append({"role": "user", "content": query})

    prev_text = ""
    for response in assistant.run(messages=messages):
        if isinstance(response, list) and response:
            last = response[-1]
            if isinstance(last, dict) and "content" in last:
                current = last["content"]
                if len(current) > len(prev_text):
                    yield current[len(prev_text):]
                    prev_text = current


def launch_webui(
    assistant: Any,
    *,
    suggestions: list[str] | None = None,
    port: int = 7860,
):
    """Launch the Qwen-Agent WebUI for interactive chat.

    Args:
        assistant: A qwen_agent.agents.Assistant instance.
        suggestions: Optional prompt suggestions shown in the UI.
        port: Gradio server port (default: 7860).
    """
    if WebUI is None:
        msg = (
            "qwen-agent WebUI requires gradio. "
            "Install: uv pip install qwen-agent[gui]"
        )
        raise ImportError(msg)

    chatbot_config = {}
    if suggestions:
        chatbot_config["prompt.suggestions"] = suggestions

    WebUI(
        assistant,
        chatbot_config=chatbot_config,
    ).run(port=port)


def create_codomyrmex_assistant(
    *,
    model: str = "qwen-coder-turbo",
    extra_tools: list[Any] | None = None,
) -> Any:
    """Create an assistant pre-configured with Codomyrmex MCP tools.

    This creates a Qwen-Agent assistant that connects to the
    Codomyrmex MCP server for code analysis, testing, and documentation.

    Args:
        model: Qwen model to use. Default: qwen-coder-turbo.
        extra_tools: Additional tools to add.

    Returns:
        Configured Assistant instance.
    """
    tools: list[Any] = ["code_interpreter"]
    if extra_tools:
        tools.extend(extra_tools)

    return create_assistant(
        model=model,
        name="Codomyrmex Code Assistant",
        description=(
            "A code assistant powered by Qwen-Coder with access to "
            "code interpreter and Codomyrmex project tools."
        ),
        tools=tools,
        system_message=(
            "You are a code assistant integrated with the Codomyrmex ecosystem. "
            "You have access to a code interpreter and can help with Python "
            "development, testing, and code analysis. Always use real, tested, "
            "functional methods. Follow the Zero-Mock policy."
        ),
    )
