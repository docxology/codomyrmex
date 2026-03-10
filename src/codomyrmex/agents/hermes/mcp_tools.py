"""MCP tool definitions for the Hermes agent module.

Exposes Hermes chat execution, skills management, and status as MCP tools.
Automatically uses Ollama hermes3 when the Hermes CLI is unavailable.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_client(
    backend: str = "auto",
    model: str = "hermes3",
    timeout: int = 120,
) -> Any:
    """Lazy-instantiate HermesClient with the given configuration.

    Args:
        backend: ``"auto"`` | ``"cli"`` | ``"ollama"``
        model: Ollama model name (default ``hermes3``)
        timeout: Subprocess timeout in seconds
    """
    from codomyrmex.agents.hermes.hermes_client import HermesClient

    return HermesClient(config={
        "hermes_backend": backend,
        "hermes_model": model,
        "hermes_timeout": timeout,
    })


@mcp_tool(
    category="hermes",
    description=(
        "Check Hermes agent availability and configuration. "
        "Reports which backend (CLI / Ollama) is active."
    ),
)
def hermes_status() -> dict[str, Any]:
    """Check Hermes configuration.

    Returns:
        dict with active_backend, cli_available, ollama_available, ollama_model
    """
    try:
        client = _get_client()
        info = client.get_hermes_status()
        return {"status": "success", "available": info.get("success", False), **info}
    except Exception as exc:
        return {"status": "error", "available": False, "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Execute a single-turn chat with the Hermes agent. "
        "Uses the Hermes CLI if available, otherwise Ollama hermes3."
    ),
)
def hermes_execute(
    prompt: str,
    backend: str = "auto",
    model: str = "hermes3",
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a prompt to the Hermes agent.

    Args:
        prompt: Natural-language task description.
        backend: ``"auto"`` (default), ``"cli"``, or ``"ollama"``.
        model: Ollama model name (default ``hermes3``).
        timeout: Subprocess timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, error, metadata
    """
    try:
        from codomyrmex.agents.core import AgentRequest

        client = _get_client(backend=backend, model=model, timeout=timeout)
        request = AgentRequest(prompt=prompt)
        response = client.execute(request)
        return {
            "status": "success" if response.is_success() else "error",
            "content": response.content,
            "error": response.error,
            "metadata": response.metadata,
        }
    except Exception as exc:
        return {"status": "error", "content": "", "error": str(exc), "metadata": {}}


@mcp_tool(
    category="hermes",
    description="List all skills available to the Hermes agent (CLI backend only).",
)
def hermes_skills_list() -> dict[str, Any]:
    """List available Hermes skills.

    Returns:
        dict with keys: status, output, or error info
    """
    try:
        client = _get_client(timeout=10)
        result = client.list_skills()
        if result.get("success"):
            return {"status": "success", "output": result.get("output", "")}
        return {"status": "error", "message": result.get("error", "Skills require CLI backend")}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description="List all available Hermes prompt template names.",
)
def hermes_template_list() -> dict[str, Any]:
    """List available Hermes prompt templates.

    Returns:
        dict with keys: status, templates (list of names), count
    """
    try:
        from codomyrmex.agents.hermes.templates import TemplateLibrary

        lib = TemplateLibrary()
        names = lib.list_templates()
        return {"status": "success", "templates": names, "count": len(names)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Render a named Hermes prompt template with variable substitution. "
        "Returns the rendered user prompt and system prompt."
    ),
)
def hermes_template_render(
    template_name: str,
    variables: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Render a Hermes prompt template.

    Args:
        template_name: Name of the built-in template (e.g. ``"code_review"``).
        variables: Optional dict of variable substitutions.  Missing variables
            are left as ``{placeholder}`` in the output (safe rendering).

    Returns:
        dict with keys: status, template_name, rendered_prompt, system_prompt, variables_used
    """
    try:
        from codomyrmex.agents.hermes.templates import TemplateLibrary

        lib = TemplateLibrary()
        template = lib.get(template_name)
        rendered = template.render_safe(**(variables or {}))
        return {
            "status": "success",
            "template_name": template_name,
            "rendered_prompt": rendered,
            "system_prompt": template.system_prompt,
            "variables_used": list((variables or {}).keys()),
        }
    except KeyError as exc:
        return {"status": "error", "message": str(exc)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Stream a response from the Hermes agent, collecting all output lines. "
        "Requires a live backend (CLI or Ollama)."
    ),
)
def hermes_stream(
    prompt: str,
    backend: str = "auto",
    model: str = "hermes3",
    timeout: int = 120,
) -> dict[str, Any]:
    """Stream Hermes agent output and collect all lines.

    Args:
        prompt: Natural-language task description.
        backend: ``"auto"`` (default), ``"cli"``, or ``"ollama"``.
        model: Ollama model name (default ``hermes3``).
        timeout: Subprocess timeout in seconds (default 120).

    Returns:
        dict with keys: status, lines (list of str), line_count, backend
    """
    try:
        from codomyrmex.agents.core import AgentRequest

        client = _get_client(backend=backend, model=model, timeout=timeout)
        if client.active_backend == "none":
            return {
                "status": "error",
                "message": "No backend available (neither hermes CLI nor ollama found)",
                "lines": [],
                "line_count": 0,
            }
        request = AgentRequest(prompt=prompt)
        lines = list(client.stream(request))
        return {
            "status": "success",
            "lines": lines,
            "line_count": len(lines),
            "backend": client.active_backend,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "lines": [], "line_count": 0}
