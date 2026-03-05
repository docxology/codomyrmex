#!/usr/bin/env python3
"""Qwen Agent Comprehensive Demo — Thin Orchestrator.

Demonstrates all QwenClient capabilities:
1. Model registry and discovery
2. Chat completion (single-turn)
3. Streaming responses
4. Tool/function calling with multi-turn loop
5. Code review via MCP tool
6. Qwen-Agent framework (if installed)

Usage:
    uv run scripts/agents/qwen/qwen_demo.py
    uv run scripts/agents/qwen/qwen_demo.py --model qwen3-max
    uv run scripts/agents/qwen/qwen_demo.py --offline  # no API calls

Requires:
    DASHSCOPE_API_KEY or QWEN_API_KEY environment variable for API calls.
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    print_warning,
    setup_logging,
)


def demo_model_registry() -> None:
    """Demo 1: Model registry and discovery."""
    print_info("\n=== 1. Model Registry ===")
    from codomyrmex.agents.qwen import DEFAULT_MODEL, QWEN_MODELS
    from codomyrmex.agents.qwen.qwen_client import QwenClient

    print_info(f"Default model: {DEFAULT_MODEL}")
    print_info(f"Total models: {len(QWEN_MODELS)}")

    print_info("\nCode-specialized models:")
    for model in QwenClient.get_code_models():
        info = QWEN_MODELS[model]
        print_success(f"  {model}: {info['context'] // 1024}K context")

    print_info("\nAll models by category:")
    categories: dict[str, list[str]] = {}
    for name, info in QWEN_MODELS.items():
        categories.setdefault(info["category"], []).append(name)
    for cat, models in sorted(categories.items()):
        print_info(f"  {cat}: {', '.join(models)}")


def demo_mcp_tools_offline() -> None:
    """Demo 2: MCP tools (offline — no API calls)."""
    print_info("\n=== 2. MCP Tools (Offline) ===")
    from codomyrmex.agents.qwen.mcp_tools import qwen_list_models

    result = qwen_list_models()
    print_success(f"qwen_list_models: {result['total']} models")
    print_info(f"  Code models: {result['code_models']}")

    # Verify all 5 tools have decorators
    from codomyrmex.agents.qwen.mcp_tools import (
        qwen_chat,
        qwen_chat_with_tools,
        qwen_code_review,
        qwen_create_agent,
    )

    for tool in [qwen_chat, qwen_chat_with_tools, qwen_list_models, qwen_create_agent, qwen_code_review]:
        name = getattr(tool, "_mcp_tool_name", "unknown")
        print_success(f"  @mcp_tool: {name}")


def demo_wrapper_functions() -> None:
    """Demo 3: Qwen-Agent wrapper function availability."""
    print_info("\n=== 3. Qwen-Agent Wrapper Functions ===")
    from codomyrmex.agents.qwen.qwen_agent_wrapper import (
        QWEN_BUILTIN_TOOLS,
        create_assistant,
        create_codomyrmex_assistant,
        launch_webui,
        run_assistant,
        stream_assistant,
    )

    print_success(f"Built-in tools: {QWEN_BUILTIN_TOOLS}")
    for fn_name, fn in [
        ("create_assistant", create_assistant),
        ("run_assistant", run_assistant),
        ("stream_assistant", stream_assistant),
        ("launch_webui", launch_webui),
        ("create_codomyrmex_assistant", create_codomyrmex_assistant),
    ]:
        print_success(f"  {fn_name}: callable={callable(fn)}")


def demo_client_construction(model: str) -> None:
    """Demo 4: QwenClient construction and capabilities."""
    print_info("\n=== 4. Client Construction ===")
    from codomyrmex.agents.qwen import QwenClient

    # Need API key for client construction
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
    if not api_key:
        print_warning("No API key — using dummy key for construction demo")
        client = QwenClient(config={"qwen_api_key": "demo-key", "qwen_model": model})
    else:
        client = QwenClient(config={"qwen_model": model})

    print_success(f"Client name: {client.name}")
    print_success(f"Base URL: {client._base_url}")
    print_info(f"Capabilities: {[c.value for c in client.capabilities]}")


def demo_chat(model: str) -> None:
    """Demo 5: Chat completion (requires API key)."""
    print_info("\n=== 5. Chat Completion ===")
    from codomyrmex.agents.core import AgentRequest
    from codomyrmex.agents.qwen import QwenClient

    client = QwenClient(config={"qwen_model": model})
    request = AgentRequest(
        prompt="Write a Python function that computes Fibonacci numbers using memoization. Include type hints.",
        system_prompt="You are a Python expert. Write clean, documented code.",
    )

    print_info(f"Model: {model}")
    print_info("Prompt: Fibonacci with memoization...")

    response = client._execute_impl(request)
    print_success(f"Response ({response.tokens_used} tokens):")
    print(response.content[:500])


def demo_streaming(model: str) -> None:
    """Demo 6: Streaming response (requires API key)."""
    print_info("\n=== 6. Streaming ===")
    from codomyrmex.agents.core import AgentRequest
    from codomyrmex.agents.qwen import QwenClient

    client = QwenClient(config={"qwen_model": model})
    request = AgentRequest(prompt="Explain Python decorators in 3 sentences.")

    print_info("Streaming: ", end="")
    for chunk in client._stream_impl(request):
        print(chunk, end="", flush=True)
    print()


def demo_tool_calling(model: str) -> None:
    """Demo 7: Tool/function calling with multi-turn loop (requires API key)."""
    print_info("\n=== 7. Tool Calling ===")
    from codomyrmex.agents.qwen import QwenClient

    client = QwenClient(config={"qwen_model": model})

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"},
                    },
                    "required": ["location"],
                },
            },
        },
    ]

    def executor(name: str, args: dict) -> str:
        if name == "get_weather":
            return f"Weather in {args.get('location', 'unknown')}: 72°F, sunny"
        return f"Unknown tool: {name}"

    messages = [{"role": "user", "content": "What's the weather in San Francisco?"}]
    result = client.chat_with_tools(
        messages=messages,
        tools=tools,
        tool_executor=executor,
        max_iterations=3,
    )

    print_success(f"Conversation: {len(result)} messages")
    for msg in result:
        role = msg.get("role", "?")
        content = msg.get("content", "")[:100]
        if msg.get("tool_calls"):
            print_info(f"  [{role}] → tool_calls: {[tc['function']['name'] for tc in msg['tool_calls']]}")
        elif role == "tool":
            print_info(f"  [{role}] {content}")
        else:
            print_info(f"  [{role}] {content}")


def demo_code_review(model: str) -> None:
    """Demo 8: Code review via MCP tool (requires API key)."""
    print_info("\n=== 8. Code Review (MCP) ===")
    from codomyrmex.agents.qwen.mcp_tools import qwen_code_review

    code = """def sort(lst):
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[j] < lst[i]:
                lst[i], lst[j] = lst[j], lst[i]
    return lst"""

    result = qwen_code_review(code=code, language="python", focus="performance", model=model)
    if result["status"] == "success":
        print_success(f"Review ({result['model']}, focus={result['focus']}):")
        print(result["review"][:400])
    else:
        print_error(f"Review failed: {result.get('error')}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Qwen Agent Comprehensive Demo")
    parser.add_argument("--model", default="qwen-coder-turbo", help="Model to use")
    parser.add_argument("--offline", action="store_true", help="Offline mode (no API calls)")
    args = parser.parse_args()

    setup_logging()
    print_info("╔══════════════════════════════════════╗")
    print_info("║   Qwen Agent Comprehensive Demo      ║")
    print_info("╚══════════════════════════════════════╝")

    # Always-available demos (no API needed)
    demo_model_registry()
    demo_mcp_tools_offline()
    demo_wrapper_functions()
    demo_client_construction(args.model)

    if args.offline:
        print_warning("\n--offline: Skipping API demos")
        return 0

    # API demos (require DASHSCOPE_API_KEY)
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
    if not api_key:
        print_warning("\nNo DASHSCOPE_API_KEY set — skipping API demos")
        print_info("Set DASHSCOPE_API_KEY to run chat, streaming, tool calling, and code review demos")
        return 0

    try:
        demo_chat(args.model)
        demo_streaming(args.model)
        demo_tool_calling(args.model)
        demo_code_review(args.model)
    except Exception as e:
        print_error(f"API demo error: {e}")
        return 1

    print_success("\n✅ All Qwen demos complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
