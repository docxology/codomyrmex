"""MCP tool definitions for the Qwen agent submodule.

Exposes Qwen-specific capabilities as MCP tools for AI agent consumption.
"""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

try:
    from codomyrmex.mcp_integration.decorators import mcp_tool
except ImportError:
    # Fallback: define a no-op decorator if MCP integration is unavailable
    def mcp_tool(*, name: str, description: str, tags: list[str] | None = None):
        def decorator(func):
            func._mcp_tool_name = name
            func._mcp_tool_description = description
            return func

        return decorator


@mcp_tool(
    name="qwen_chat",
    description=(
        "Send a chat message to a Qwen model (DashScope API). "
        "Returns the model response. Supports all Qwen variants."
    ),
    tags=["qwen", "llm", "chat"],
)
def qwen_chat(
    message: str,
    *,
    model: str = "qwen-coder-turbo",
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> dict[str, Any]:
    """Chat with a Qwen model.

    Args:
        message: User message to send.
        model: Qwen model name.
        system_prompt: Optional system message.
        temperature: Sampling temperature.
        max_tokens: Maximum response tokens.

    Returns:
        dict with 'content', 'model', 'tokens_used', 'finish_reason'.
    """
    from codomyrmex.agents.core import AgentRequest

    from .qwen_client import QwenClient

    client = QwenClient(
        config={
            "qwen_model": model,
            "qwen_temperature": temperature,
            "qwen_max_tokens": max_tokens,
        }
    )

    request = AgentRequest(
        prompt=message,
        **({"context": {"system_prompt": system_prompt}} if system_prompt else {}),
    )

    try:
        response = client._execute_impl(request)
        return {
            "content": response.content,
            "model": model,
            "tokens_used": response.tokens_used,
            "finish_reason": response.metadata.get("finish_reason"),
            "status": "success",
        }
    except Exception as e:
        logger.error("qwen_chat error: %s", e)
        return {"content": "", "error": str(e), "status": "error"}


@mcp_tool(
    name="qwen_chat_with_tools",
    description=(
        "Run a multi-turn tool-calling conversation with Qwen. "
        "Provide tool definitions in OpenAI format."
    ),
    tags=["qwen", "llm", "tools", "function-calling"],
)
def qwen_chat_with_tools(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    *,
    model: str = "qwen3-max",
    max_iterations: int = 5,
) -> dict[str, Any]:
    """Run a tool-calling conversation loop.

    Args:
        messages: Initial conversation messages.
        tools: OpenAI-format tool definitions.
        model: Qwen model name.
        max_iterations: Maximum tool-calling rounds.

    Returns:
        dict with 'messages' (full conversation) and 'status'.
    """
    from .qwen_client import QwenClient

    client = QwenClient(config={"qwen_model": model})

    try:
        result = client.chat_with_tools(
            messages=messages,
            tools=tools,
            max_iterations=max_iterations,
        )
        return {"messages": result, "status": "success"}
    except Exception as e:
        logger.error("qwen_chat_with_tools error: %s", e)
        return {"messages": messages, "error": str(e), "status": "error"}


@mcp_tool(
    name="qwen_list_models",
    description="list all available Qwen models with their context lengths and categories.",
    tags=["qwen", "models", "registry"],
)
def qwen_list_models() -> dict[str, Any]:
    """list available Qwen models.

    Returns:
        dict with 'models' containing model registry and 'code_models' list.
    """
    from .qwen_client import QWEN_MODELS, QwenClient

    return {
        "models": QWEN_MODELS,
        "code_models": QwenClient.get_code_models(),
        "total": len(QWEN_MODELS),
    }


@mcp_tool(
    name="qwen_create_agent",
    description=(
        "Create a Qwen-Agent framework Assistant with optional MCP server "
        "integration and built-in tools like code_interpreter."
    ),
    tags=["qwen", "agent", "qwen-agent", "mcp"],
)
def qwen_create_agent(
    *,
    model: str = "qwen-coder-turbo",
    tools: list[str] | None = None,
    system_message: str = "",
) -> dict[str, Any]:
    """Create a Qwen-Agent assistant.

    Args:
        model: Model name (default: qwen-coder-turbo).
        tools: list of tool names (e.g., ['code_interpreter', 'image_gen']).
        system_message: System prompt.

    Returns:
        dict with 'status' and 'agent_info'.
    """
    try:
        from .qwen_agent_wrapper import create_assistant

        create_assistant(
            model=model,
            tools=tools,
            system_message=system_message,
        )
        return {
            "status": "success",
            "agent_info": {
                "model": model,
                "tools": tools or [],
                "type": "qwen_agent.Assistant",
            },
        }
    except ImportError as e:
        return {"status": "error", "error": str(e)}


@mcp_tool(
    name="qwen_code_review",
    description=(
        "Submit code to Qwen-Coder for review. Returns analysis, "
        "suggestions, and potential issues."
    ),
    tags=["qwen", "code-review", "analysis"],
)
def qwen_code_review(
    code: str,
    *,
    language: str = "python",
    focus: str = "general",
    model: str = "qwen-coder-turbo",
) -> dict[str, Any]:
    """Review code using Qwen-Coder.

    Args:
        code: Source code to review.
        language: Programming language.
        focus: Review focus ('general', 'security', 'performance', 'style').
        model: Qwen model to use.

    Returns:
        dict with 'review' content and metadata.
    """
    from codomyrmex.agents.core import AgentRequest

    from .qwen_client import QwenClient

    system_prompt = (
        f"You are an expert {language} code reviewer. "
        f"Focus on: {focus}. "
        "Provide specific, actionable feedback with line references."
    )

    client = QwenClient(
        config={
            "qwen_model": model,
            "qwen_max_tokens": 4096,
        }
    )

    request = AgentRequest(
        prompt=f"""Review the following {language} code:

```{language}
{code}
```""",
        **({"context": {"system_prompt": system_prompt}} if system_prompt else {}),
    )

    try:
        response = client._execute_impl(request)
        return {
            "review": response.content,
            "model": model,
            "language": language,
            "focus": focus,
            "status": "success",
        }
    except Exception as e:
        logger.error("qwen_code_review error: %s", e)
        return {"review": "", "error": str(e), "status": "error"}
