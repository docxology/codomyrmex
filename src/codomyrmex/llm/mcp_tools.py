"""MCP tools for the LLM module."""

from __future__ import annotations

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="llm")
def generate_text(
    prompt: str, provider: str = "openrouter", model: str = "openrouter/free"
) -> dict:
    """Generate text using a specified LLM provider and model.

    Args:
        prompt: The input prompt for the LLM
        provider: The provider to use (e.g., 'openrouter', 'ollama')
        model: The specific model ID to use

    Returns:
        Structured response with the generated text.
    """
    if provider == "openrouter":
        try:
            response = ask(question=prompt, model=model)
            if response.startswith("Error:"):
                return {"status": "error", "message": response}
            return {"status": "success", "content": response}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    elif provider == "ollama":
        try:
            from codomyrmex.llm import OllamaManager

            manager = OllamaManager()
            result = manager.generate(prompt=prompt, model=model)
            return {"status": "success", "content": result.get("response", "")}
        except Exception as e:
            return {"status": "error", "message": f"Ollama generation failed: {e}"}

    return {"status": "error", "message": f"Unsupported provider: {provider}"}


@mcp_tool(category="llm")
def list_local_models() -> dict:
    """List available local models managed by Ollama.

    Returns:
        List of local LLM models installed.
    """
    from codomyrmex.llm import OllamaManager

    try:
        manager = OllamaManager()
        models = manager.list_models()
        return {
            "status": "success",
            "models": [m.get("name") for m in models],
            "count": len(models),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to list local models: {e}"}


@mcp_tool(category="llm")
def query_fabric_metadata() -> dict:
    """Query configuration metadata for Microsoft Fabric integration.

    Returns:
        Fabric connection configuration metadata.
    """
    from codomyrmex.llm import FabricManager

    try:
        manager = FabricManager()
        if not manager.is_configured():
            return {
                "status": "success",
                "configured": False,
                "message": "Fabric is not configured currently.",
            }

        settings = manager.get_current_settings()
        return {
            "status": "success",
            "configured": True,
            "workspace": settings.get("workspace_id"),
            "tenant": settings.get("tenant_id"),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to query Fabric metadata: {e}"}


@mcp_tool(category="llm")
def reason(prompt: str, depth: str = "normal", max_steps: int = 5) -> dict:
    """Run Chain-of-Thought reasoning on a prompt.

    Decomposes the prompt into systematic reasoning steps and synthesizes
    a conclusion with confidence scoring.

    Args:
        prompt: The question or problem to reason about.
        depth: Reasoning depth -- "shallow" (1 step), "normal" (3 steps), "deep" (5 steps).
        max_steps: Maximum reasoning steps (overrides depth if specified).

    Returns:
        dict with: steps (list of reasoning steps), conclusion (str), confidence (float 0-1),
                   step_count (int), depth (str).
    """
    try:
        from codomyrmex.llm.chain_of_thought import ChainOfThought
        from codomyrmex.llm.models.reasoning import ThinkingDepth

        depth_map = {
            "shallow": ThinkingDepth.SHALLOW,
            "normal": ThinkingDepth.NORMAL,
            "deep": ThinkingDepth.DEEP,
            "exhaustive": ThinkingDepth.EXHAUSTIVE,
        }
        thinking_depth = depth_map.get(depth, ThinkingDepth.NORMAL)

        cot = ChainOfThought(depth=thinking_depth)
        trace = cot.think(prompt)

        return {
            "status": "success",
            "steps": [
                {
                    "step": i + 1,
                    "type": s.step_type,
                    "content": s.thought,
                    "confidence": s.confidence,
                }
                for i, s in enumerate(trace.steps)
            ],
            "conclusion": trace.conclusion.action if trace.conclusion else str(trace),
            "confidence": trace.total_confidence,
            "step_count": trace.step_count,
            "depth": depth,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="llm")
def ask(question: str, model: str = "openrouter/free") -> str:
    """Ask a question to an LLM provider (default: OpenRouter Free Tier).

    Args:
        question: The prompt/question to ask
        model: Model to use (default: openrouter/free)

    Returns:
        The text response from the LLM.
    """
    import os

    from codomyrmex.llm.providers import (
        Message,
        ProviderConfig,
        ProviderType,
        get_provider,
    )

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
