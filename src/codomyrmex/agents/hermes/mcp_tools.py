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


@mcp_tool(
    category="hermes",
    description=(
        "Execute a persistent, multi-turn chat with the Hermes agent. "
        "Each call with the same session_id appends to the conversation history."
    ),
)
def hermes_chat_session(
    prompt: str,
    session_id: str | None = None,
    backend: str = "auto",
    model: str = "hermes3",
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a prompt to a stateful Hermes agent session.

    Args:
        prompt: Natural-language task description.
        session_id: Session ID to continue, or None to start a new one.
        backend: ``"auto"`` (default), ``"cli"``, or ``"ollama"``.
        model: Ollama model name (default ``hermes3``).
        timeout: Subprocess timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, session_id, error, metadata
    """
    try:
        client = _get_client(backend=backend, model=model, timeout=timeout)
        response = client.chat_session(prompt=prompt, session_id=session_id)
        return {
            "status": "success" if response.is_success() else "error",
            "content": response.content,
            "session_id": response.metadata.get("session_id"),
            "error": response.error,
            "metadata": response.metadata,
        }
    except Exception as exc:
        return {"status": "error", "content": "", "session_id": None, "error": str(exc), "metadata": {}}


@mcp_tool(
    category="hermes",
    description="List all active persistent Hermes session IDs.",
)
def hermes_session_list() -> dict[str, Any]:
    """List available Hermes session IDs.

    Returns:
        dict with keys: status, sessions (list of str), count
    """
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore
        client = _get_client()
        with SQLiteSessionStore(client._session_db_path) as store:
            sessions = store.list_sessions()
            return {"status": "success", "sessions": sessions, "count": len(sessions)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description="Clear a specific Hermes chat session by ID.",
)
def hermes_session_clear(session_id: str) -> dict[str, Any]:
    """Delete a Hermes session.

    Args:
        session_id: ID of the session to delete.

    Returns:
        dict with keys: status, deleted, message
    """
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore
        client = _get_client()
        with SQLiteSessionStore(client._session_db_path) as store:
            deleted = store.delete(session_id)
            return {"status": "success", "deleted": deleted, "message": f"Deleted session {session_id}" if deleted else f"Session {session_id} not found."}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Submit a sampling request to the Hermes agent. "
        "Simulates server-initiated sampling where the MCP server asks Hermes "
        "to generate a completion for a given prompt and context."
    ),
)
def hermes_sampling(
    prompt: str,
    system_prompt: str = "",
    max_tokens: int = 2048,
    backend: str = "auto",
    model: str = "hermes3",
) -> dict[str, Any]:
    """Server-initiated sampling via Hermes.

    This implements the MCP sampling protocol where a server can request
    the client (Hermes) to generate a completion.

    Args:
        prompt: The sampling prompt from the MCP server.
        system_prompt: Optional system prompt to guide generation.
        max_tokens: Maximum tokens to generate.
        backend: ``"auto"`` (default), ``"cli"``, or ``"ollama"``.
        model: Ollama model name (default ``hermes3``).

    Returns:
        dict with keys: status, content, model, stop_reason, usage
    """
    try:
        from codomyrmex.agents.core import AgentRequest

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        client = _get_client(backend=backend, model=model, timeout=120)
        request = AgentRequest(prompt=full_prompt)
        response = client.execute(request)

        if response.is_success():
            content = response.content
            # Truncate to approximate max_tokens
            chars_limit = max_tokens * 4  # rough chars/token
            if len(content) > chars_limit:
                content = content[:chars_limit]
                stop_reason = "max_tokens"
            else:
                stop_reason = "end_turn"

            return {
                "status": "success",
                "content": content,
                "model": response.metadata.get("model", model),
                "stop_reason": stop_reason,
                "usage": {
                    "prompt_chars": len(full_prompt),
                    "completion_chars": len(content),
                },
            }
        return {"status": "error", "content": "", "error": response.error}
    except Exception as exc:
        return {"status": "error", "content": "", "error": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Hot-reload the Hermes MCP server configuration. "
        "Re-reads ~/.hermes/mcp_servers.json and signals Hermes to reconnect."
    ),
)
def hermes_mcp_reload() -> dict[str, Any]:
    """Hot-reload MCP server configuration.

    Returns:
        dict with keys: status, servers_loaded, output
    """
    try:
        from codomyrmex.agents.hermes._provider_router import MCPBridgeManager
        bridge = MCPBridgeManager()
        result = bridge.reload()
        return {"status": "success", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Manage cross-session user context for the Hermes agent. "
        "Stores and retrieves user preferences and coding observations."
    ),
)
def hermes_user_context(
    action: str = "get",
    key: str | None = None,
    value: str | None = None,
) -> dict[str, Any]:
    """Manage Hermes cross-session user model.

    Args:
        action: ``"get"`` to retrieve context, ``"set"`` to set a preference,
            ``"observe"`` to record an observation.
        key: Preference key (for ``"set"`` action).
        value: Value to set or observation text.

    Returns:
        dict with keys: status, context or preference data
    """
    try:
        from codomyrmex.agents.hermes._provider_router import UserModel
        model = UserModel()

        if action == "get":
            return {
                "status": "success",
                "context_prompt": model.get_context_prompt(),
                "profile": model.profile,
            }
        if action == "set" and key and value:
            model.set_preference(key, value)
            return {"status": "success", "message": f"Set {key}={value}"}
        if action == "observe" and value:
            model.add_observation(value)
            return {"status": "success", "message": f"Recorded observation: {value[:60]}..."}
        return {"status": "error", "message": f"Invalid action '{action}' or missing key/value"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description="Run hermes doctor for comprehensive health diagnostics (CLI v0.2.0+).",
)
def hermes_doctor() -> dict[str, Any]:
    """Run Hermes health diagnostics.

    Returns:
        dict with keys: status, output, stderr, exit_code
    """
    try:
        client = _get_client()
        result = client.run_doctor()
        return {"status": "success" if result.get("success") else "error", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description="Get the installed Hermes CLI version string.",
)
def hermes_version() -> dict[str, Any]:
    """Get Hermes CLI version.

    Returns:
        dict with keys: status, version
    """
    try:
        client = _get_client()
        version = client.get_version()
        return {
            "status": "success" if version else "unavailable",
            "version": version,
            "cli_available": client._cli_available,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Create an isolated git worktree for a Hermes session, "
        "enabling parallel agent execution without branch conflicts."
    ),
)
def hermes_worktree_create(session_id: str) -> dict[str, Any]:
    """Create an isolated git worktree for a session.

    Args:
        session_id: Session identifier for the worktree branch name.

    Returns:
        dict with keys: status, worktree_path, branch_name
    """
    try:
        client = _get_client()
        path = client.create_worktree(session_id)
        if path:
            return {
                "status": "success",
                "worktree_path": str(path),
                "branch_name": f"hermes/{session_id}",
            }
        return {"status": "error", "message": "Failed to create worktree"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description="Remove an isolated git worktree after a session completes.",
)
def hermes_worktree_cleanup(session_id: str) -> dict[str, Any]:
    """Clean up a git worktree for a session.

    Args:
        session_id: Session identifier matching the worktree.

    Returns:
        dict with keys: status, cleaned
    """
    try:
        client = _get_client()
        cleaned = client.cleanup_worktree(session_id)
        return {"status": "success" if cleaned else "error", "cleaned": cleaned}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description="Search Hermes sessions by name substring.",
)
def hermes_session_search(query: str) -> dict[str, Any]:
    """Search sessions by name.

    Args:
        query: Substring to match against session names.

    Returns:
        dict with keys: status, sessions, count
    """
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        client = _get_client()
        with SQLiteSessionStore(client._session_db_path) as store:
            results = store.search_sessions(query)
            return {"status": "success", "sessions": results, "count": len(results)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Check the status of the Honcho AI memory integration. "
        "Honcho provides persistent cross-session memory for Hermes."
    ),
)
def hermes_honcho_status() -> dict[str, Any]:
    """Check Honcho memory integration status.

    Returns:
        dict with keys: status, output, exit_code
    """
    try:
        import os
        import shutil
        import subprocess

        hermes_bin = shutil.which("hermes")
        if not hermes_bin:
            return {"status": "error", "message": "Hermes CLI not available"}

        result = subprocess.run(
            [hermes_bin, "honcho", "status"],
            capture_output=True, text=True, timeout=15,
            env={**os.environ, "NO_COLOR": "1"},
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "honcho status timed out"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Show Hermes usage insights and analytics — token usage, costs, "
        "tool patterns, and activity trends."
    ),
)
def hermes_insights(days: int = 30) -> dict[str, Any]:
    """Get Hermes usage insights.

    Args:
        days: Number of days to analyze (default 30).

    Returns:
        dict with keys: status, output, exit_code
    """
    try:
        import os
        import shutil
        import subprocess

        hermes_bin = shutil.which("hermes")
        if not hermes_bin:
            return {"status": "error", "message": "Hermes CLI not available"}

        result = subprocess.run(
            [hermes_bin, "insights", "--days", str(days)],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "NO_COLOR": "1"},
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "insights timed out"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Get the credential and availability status for all configured "
        "inference providers (OpenRouter, Ollama, Anthropic, etc.)."
    ),
)
def hermes_provider_status() -> dict[str, Any]:
    """Check multi-provider credential status.

    Returns:
        dict with keys: status, providers (dict per provider)
    """
    try:
        from codomyrmex.agents.hermes._provider_router import ProviderRouter

        router = ProviderRouter()
        return {"status": "success", "providers": router.get_provider_status()}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

