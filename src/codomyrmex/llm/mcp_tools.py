"""MCP tools for the LLM module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="llm")
def generate_text(prompt: str, provider: str = "openrouter", model: str = "openrouter/free") -> dict:
    """Generate text using a specified LLM provider and model.

    Args:
        prompt: The input prompt for the LLM
        provider: The provider to use (e.g., 'openrouter', 'ollama')
        model: The specific model ID to use

    Returns:
        Structured response with the generated text.
    """
    if provider == "openrouter":
        from codomyrmex.llm import ask
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
        return {"status": "success", "models": [m.get("name") for m in models], "count": len(models)}
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
            return {"status": "success", "configured": False, "message": "Fabric is not configured currently."}

        settings = manager.get_current_settings()
        return {
            "status": "success",
            "configured": True,
            "workspace": settings.get("workspace_id"),
            "tenant": settings.get("tenant_id")
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to query Fabric metadata: {e}"}
