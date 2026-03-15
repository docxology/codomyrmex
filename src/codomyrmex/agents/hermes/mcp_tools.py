"""MCP tool definitions for the Hermes agent module.

Exposes Hermes chat execution, skills management, and status as MCP tools.
Automatically uses Ollama hermes3 when the Hermes CLI is unavailable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

if TYPE_CHECKING:
    from codomyrmex.agents.hermes.hermes_client import HermesClient


@mcp_tool(
    category="hermes",
    description=(
        "Search the agentic memory (SQLite FTS5) for past conversational context. "
        "Use this when you need to recall past decisions or specific topics discussed previously."
    ),
)
def hermes_recall_memory(query: str, limit: int = 10) -> dict[str, Any]:
    """Search for past session text using FTS BM25 ranking.

    Args:
        query: Full-text search string (supports SQLite MATCH syntax).
        limit: Number of results to return (default 10).

    Returns:
        dict with status, and results list containing matched snippets.
    """
    try:
        import os
        from pathlib import Path

        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        # Load the DB path the same way the client does
        WORKSPACE_ROOT = Path(os.path.abspath(".")).resolve()
        db_path = WORKSPACE_ROOT / ".codomyrmex" / "hermes_sessions.db"

        with SQLiteSessionStore(db_path) as store:
            results = store.search_fts(query, limit)
            return {
                "status": "success",
                "count": len(results),
                "results": results,
            }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "results": []}


def _get_client(
    backend: str = "auto",
    model: str = "hermes3",
    timeout: int = 120,
) -> HermesClient:
    """Lazy-instantiate HermesClient with the given configuration.

    Args:
        backend: ``"auto"`` | ``"cli"`` | ``"ollama"``
        model: Ollama model name (default ``hermes3``)
        timeout: Subprocess timeout in seconds
    """
    from codomyrmex.agents.hermes.hermes_client import HermesClient

    return HermesClient(
        config={
            "hermes_backend": backend,
            "hermes_model": model,
            "hermes_timeout": timeout,
        }
    )


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
        "Check live system resource metrics (RAM, CPU, Swap). "
        "Use this proactively to check if the host has enough memory before dispatching heavy tasks."
    ),
)
def hermes_system_health() -> dict[str, Any]:
    """Retrieve realtime hardware usage metrics.

    Returns:
        dict with keys: status, metrics (cpu_percent, ram_usage_percent, swap_usage_percent)
    """
    try:
        from codomyrmex.agents.hermes.monitoring import _get_system_metrics

        metrics = _get_system_metrics()
        return {
            "status": "success",
            "metrics": metrics,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Check if a dependency is present in the project's lockfile (`uv.lock`). "
        "Use this to verify if uninstalled packages are causing execution failures."
    ),
)
def hermes_check_dependencies(package_name: str) -> dict[str, Any]:
    """Check for package presence in the environment lockfile.

    Args:
        package_name: The name of the PyPI package to check (e.g. 'requests').

    Returns:
        dict with status, exists boolean, and message.
    """
    try:
        from codomyrmex.environment_setup.lockfile import LockfileParser

        parser = LockfileParser()
        exists = parser.check_dependency(package_name)
        return {
            "status": "success",
            "package": package_name,
            "exists": exists,
            "message": f"Package '{package_name}' is {'present' if exists else 'missing'} in the uv.lock",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


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
        return {
            "status": "error",
            "message": result.get("error", "Skills require CLI backend"),
        }
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
        "Initiate an autonomous red/green/refactor coverage loop on a target filepath. "
        "The system will repeatedly run pytest and repair the codebase until the tests pass."
    ),
)
def hermes_run_coverage_loop(target_filepath: str) -> dict[str, Any]:
    """Autonomous pytest healing loop.

    Args:
        target_filepath: The path to the test file or directory to verify.

    Returns:
        dict containing status, number of turns taken, and output trace.
    """
    try:
        # Load the client explicitly configured for the current repository
        client = _get_client()
        result = client._run_coverage_loop(target_filepath)
        return result
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
        return {
            "status": "error",
            "content": "",
            "session_id": None,
            "error": str(exc),
            "metadata": {},
        }


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
            return {
                "status": "success",
                "deleted": deleted,
                "message": f"Deleted session {session_id}"
                if deleted
                else f"Session {session_id} not found.",
            }
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
            return {
                "status": "success",
                "message": f"Recorded observation: {value[:60]}...",
            }
        return {
            "status": "error",
            "message": f"Invalid action '{action}' or missing key/value",
        }
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
            capture_output=True,
            text=True,
            timeout=15,
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
            capture_output=True,
            text=True,
            timeout=30,
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


@mcp_tool(
    category="hermes",
    description=(
        "Parse an Obsidian Canvas (.canvas) file into a structured dictionary "
        "of textual nodes and connections, useful for reading architecture diagrams."
    ),
)
def hermes_parse_canvas(vault_path: str, canvas_name: str) -> dict[str, Any]:
    """Parse an Obsidian Canvas into a readable node graph.

    Args:
        vault_path: Path to the Obsidian vault root directory.
        canvas_name: Name or relative path of the .canvas file.

    Returns:
        dict with keys: status, nodes (list), edges (list), error (if any)
    """
    try:
        import os
        from pathlib import Path

        from codomyrmex.agentic_memory.obsidian.canvas import parse_canvas
        from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault

        expanded = Path(os.path.expanduser(vault_path)).resolve()
        vault = ObsidianVault(expanded)

        if not canvas_name.endswith(".canvas"):
            canvas_name += ".canvas"

        canvas_path = vault.path / canvas_name
        if not canvas_path.exists():
            return {"status": "error", "message": f"Canvas not found at {canvas_path}"}

        canvas = parse_canvas(canvas_path)

        # Format the nodes and edges for LLM consumption
        nodes = []
        for node in canvas.nodes:
            if node.type == "text":
                nodes.append({"id": node.id, "type": "text", "content": node.text})
            elif node.type == "file":
                nodes.append({"id": node.id, "type": "file", "file": node.file})
            elif node.type == "link":
                nodes.append({"id": node.id, "type": "link", "url": node.url})

        edges = []
        for edge in canvas.edges:
            edges.append(
                {
                    "id": edge.id,
                    "fromNode": edge.fromNode,
                    "toNode": edge.toNode,
                    "label": edge.label or "",
                }
            )

        return {
            "status": "success",
            "nodes": nodes,
            "edges": edges,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Search the Obsidian Vault for historical sessions, context, or facts "
        "using full-text indexing or optional regex. Useful for long-term RAG."
    ),
)
def hermes_search_vault(
    vault_path: str, query: str, use_regex: bool = False
) -> dict[str, Any]:
    """Search the specified Obsidian vault.

    Args:
        vault_path: Path to the Obsidian vault root directory.
        query: Search string or regex pattern.
        use_regex: Set to True to treat the query as a regular expression.

    Returns:
        dict with keys: status, results (list of snippets), count, error (if any)
    """
    try:
        import os
        from pathlib import Path

        from codomyrmex.agentic_memory.obsidian.search import search_regex, search_vault
        from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault

        expanded = Path(os.path.expanduser(vault_path)).resolve()
        vault = ObsidianVault(expanded)

        if use_regex:
            results = search_regex(vault, query)
        else:
            results = search_vault(vault, query)

        formatted = []
        for res in results:
            formatted.append({"note": res.note.title, "matches": res.context})

        return {
            "status": "success",
            "results": formatted,
            "count": len(formatted),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Create a stateful workflow task for this session. "
        "Allows Hermes to break down complex instructions into explicit checklists."
    ),
)
def hermes_create_task(
    session_id: str,
    name: str,
    description: str,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    """Create an internal orchestration task.

    Args:
        session_id: The current Hermes session ID.
        name: A short unique identifier for the task (e.g., "setup_db").
        description: Details of the task to be performed.
        depends_on: Optional list of task names this task depends on.

    Returns:
        dict with keys: status, task
    """
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        client = _get_client()
        with SQLiteSessionStore(client._session_db_path) as store:
            session = store.load(session_id)
            if not session:
                return {
                    "status": "error",
                    "message": f"Session {session_id} not found.",
                }

            tasks = session.metadata.get("workflow_tasks", {})

            if name in tasks:
                return {"status": "error", "message": f"Task '{name}' already exists."}

            from codomyrmex.logging_monitoring.core.correlation import (
                get_correlation_id,
            )

            new_task = {
                "name": name,
                "description": description,
                "depends_on": depends_on or [],
                "status": "pending",
                "result": None,
                "error": "",
                "parent_trace_id": get_correlation_id(),
            }
            tasks[name] = new_task
            session.metadata["workflow_tasks"] = tasks

            store.save(session)
            return {"status": "success", "task": new_task}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Update the status of a stateful workflow task. "
        "Use this as you progress through your self-created checklist."
    ),
)
def hermes_update_task_status(
    session_id: str,
    name: str,
    status: str,
    result: str = "",
    error: str = "",
) -> dict[str, Any]:
    """Update a task's status in the current session workflow.

    Args:
        session_id: The current Hermes session ID.
        name: The task identifier to update.
        status: The new status (e.g., "running", "completed", "failed").
        result: Optional result summary to store.
        error: Optional error message if failed.

    Returns:
        dict with keys: status, task, message
    """
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        client = _get_client()
        with SQLiteSessionStore(client._session_db_path) as store:
            session = store.load(session_id)
            if not session:
                return {
                    "status": "error",
                    "message": f"Session {session_id} not found.",
                }

            tasks = session.metadata.get("workflow_tasks", {})

            if name not in tasks:
                return {"status": "error", "message": f"Task '{name}' not found."}

            task = tasks[name]
            task["status"] = status
            if result:
                task["result"] = result
            if error:
                task["error"] = error

            session.metadata["workflow_tasks"] = tasks
            store.save(session)

            return {"status": "success", "task": task}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Delegate heavy processing back to an ephemeral sub-agent. "
        "Allows Hermes to spin up an isolated reasoning session (e.g. Jules or Claude) "
        "to process a specific file or task without bloating Hermes' own context window."
    ),
)
def hermes_delegate_task(
    directive: str,
    context_file: str = "",
    agent_type: str = "jules",
) -> dict[str, Any]:
    """Delegate a reasoning task to a sub-agent.

    Args:
        directive: Specific command for the sub-agent (e.g. "Summarize this module").
        context_file: Absolute path to a file to inject as context payload.
        agent_type: The sub-agent class to use (e.g., "jules" or "claude"). Defaults to "jules".

    Returns:
        dict with keys: status, sub_agent_response, execution_time_seconds
    """
    import time
    from pathlib import Path

    try:
        from codomyrmex.agents.core import AgentRequest

        start_time = time.time()
        file_payload = ""

        if context_file:
            path = Path(context_file)
            if not path.is_absolute():
                return {
                    "status": "error",
                    "message": "context_file must be an absolute path.",
                }
            if not path.exists():
                return {"status": "error", "message": f"File not found: {context_file}"}
            file_payload = f"\n\nContext File ({path.name}):\n```\n{path.read_text(encoding='utf-8')}\n```\n"

        full_prompt = (
            f"You are a delegated sub-agent sub-routine running inside Codomyrmex.\n"
            f"Your parent agent has deferred a specific task to you.\n"
            f"Fulfill the following directive meticulously based on the provided context.\n\n"
            f"Directive: {directive}{file_payload}"
        )

        sub_agent = None
        if agent_type.lower() == "jules":
            from codomyrmex.agents.jules import JulesClient

            sub_agent = JulesClient()
        elif agent_type.lower() == "claude":
            from codomyrmex.agents.claude import ClaudeClient

            sub_agent = ClaudeClient()
        else:
            return {
                "status": "error",
                "message": f"Unsupported agent_type: {agent_type}",
            }

        request = AgentRequest(prompt=full_prompt)
        from codomyrmex.logging_monitoring.core.correlation import get_correlation_id

        parent_cid = get_correlation_id()
        if parent_cid:
            request.metadata["parent_trace_id"] = parent_cid

        response = sub_agent.execute(request)

        return {
            "status": "success" if response.is_success() else "error",
            "sub_agent_response": response.content,
            "error": response.error,
            "execution_time_seconds": round(time.time() - start_time, 2),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "sub_agent_response": ""}


@mcp_tool(
    category="hermes",
    description=(
        "Read a specific chunk of a large log file. "
        "Useful for paginating through massive stack traces or outputs."
    ),
)
def hermes_read_log_chunk(
    file_path: str,
    offset: int = 0,
    length: int = 500,
) -> dict[str, Any]:
    """Read a segment of lines from a cached log file natively.

    Args:
        file_path: Absolute path to the cached log file.
        offset: Line number to start reading from (0-indexed).
        length: Number of lines to read (max 5000).

    Returns:
        dict with keys: status, content, total_lines, eof
    """
    import os

    try:
        length = min(length, 5000)

        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}

        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        total_lines = len(lines)
        end_idx = min(offset + length, total_lines)
        chunk = "".join(lines[offset:end_idx])

        return {
            "status": "success",
            "content": chunk,
            "total_lines": total_lines,
            "eof": end_idx >= total_lines,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# New session management tools (v1.5.x+)
# ---------------------------------------------------------------------------


@mcp_tool(
    category="hermes",
    description=(
        "Return summary statistics about the Hermes session database: "
        "session count, disk size, and timestamps of oldest and newest sessions."
    ),
)
def hermes_session_stats() -> dict[str, Any]:
    """Get Hermes session database statistics.

    Returns:
        dict with keys: status, session_count, db_size_bytes,
        oldest_session_at, newest_session_at
    """
    try:
        client = _get_client()
        stats = client.get_session_stats()
        return {"status": "success", **stats}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Fork an existing Hermes session into an independent child session. "
        "The child inherits the full message history and can diverge independently."
    ),
)
def hermes_session_fork(
    session_id: str,
    new_name: str | None = None,
) -> dict[str, Any]:
    """Fork a Hermes session.

    Args:
        session_id: Source session to fork.
        new_name: Optional name for the child session.

    Returns:
        dict with keys: status, child_session_id, name, parent_session_id
    """
    try:
        client = _get_client()
        child = client.fork_session(session_id, new_name=new_name)
        if child is None:
            return {"status": "error", "message": f"Session {session_id!r} not found"}
        return {
            "status": "success",
            "child_session_id": child.session_id,
            "name": child.name,
            "parent_session_id": child.parent_session_id,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Export a Hermes session as formatted Markdown text. "
        "Useful for archiving conversations or sharing context with other agents."
    ),
)
def hermes_session_export_md(session_id: str) -> dict[str, Any]:
    """Export a Hermes session as Markdown.

    Args:
        session_id: Session to export.

    Returns:
        dict with keys: status, markdown, session_id
    """
    try:
        client = _get_client()
        md = client.export_session_markdown(session_id)
        if md is None:
            return {"status": "error", "message": f"Session {session_id!r} not found"}
        return {"status": "success", "session_id": session_id, "markdown": md}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Submit a list of prompts to the Hermes agent and collect all results. "
        "Optionally runs prompts in parallel for faster throughput."
    ),
)
def hermes_batch_execute(
    prompts: list[str],
    parallel: bool = False,
    backend: str = "auto",
    timeout: int = 120,
) -> dict[str, Any]:
    """Execute a batch of prompts with the Hermes agent.

    Args:
        prompts: List of prompt strings to process.
        parallel: Submit all prompts concurrently (default False).
        backend: ``"auto"`` (default), ``"cli"``, or ``"ollama"``.
        timeout: Per-prompt timeout in seconds (default 120).

    Returns:
        dict with keys: status, results (list of {prompt, status, content, error}), count
    """
    try:
        client = _get_client(backend=backend, timeout=timeout)
        results = client.batch_execute(prompts, parallel=parallel)
        total_err = sum(1 for r in results if r["status"] == "error")
        return {
            "status": "success" if total_err == 0 else "partial",
            "results": results,
            "count": len(results),
            "errors": total_err,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "results": [], "count": 0}


@mcp_tool(
    category="hermes",
    description=(
        "Set or replace the persistent system prompt for a Hermes session. "
        "The system prompt is always the first message and guides agent behaviour."
    ),
)
def hermes_set_system_prompt(
    session_id: str,
    prompt: str,
) -> dict[str, Any]:
    """Set the system prompt for a Hermes session.

    Args:
        session_id: Session to update (will be created if missing).
        prompt: System instruction text.

    Returns:
        dict with keys: status, session_id, message
    """
    try:
        client = _get_client()
        ok = client.set_system_prompt(session_id, prompt)
        return {
            "status": "success" if ok else "error",
            "session_id": session_id,
            "message": "System prompt set" if ok else "Failed to set system prompt",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Retrieve full detail about a specific Hermes session, including "
        "message count, last message, system prompt flag, and all metadata."
    ),
)
def hermes_session_detail(session_id: str) -> dict[str, Any]:
    """Get detailed information about a Hermes session.

    Args:
        session_id: Session to describe.

    Returns:
        dict with keys: status, session_id, name, message_count, last_message,
        has_system_prompt, metadata, created_at, updated_at
    """
    try:
        client = _get_client()
        detail = client.get_session_detail(session_id)
        if detail is None:
            return {"status": "error", "message": f"Session {session_id!r} not found"}
        return {"status": "success", **detail}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Archive and delete Hermes sessions older than the specified number of days. "
        "Archived sessions are gzip-compressed and saved to sessions_archive/ next to the DB."
    ),
)
def hermes_prune_sessions(days_old: int = 30) -> dict[str, Any]:
    """Archive and prune old Hermes sessions.

    Args:
        days_old: Remove sessions not updated within this many days (default 30).

    Returns:
        dict with keys: status, pruned_count, message
    """
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        client = _get_client()
        with SQLiteSessionStore(client._session_db_path) as store:
            count = store.prune_old_sessions(days_old=days_old)
        return {
            "status": "success",
            "pruned_count": count,
            "message": f"Archived and deleted {count} sessions older than {days_old} days.",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Check the current model rotation state, including health, priorities, "
        "and active cooldown periods for free OpenRouter models."
    ),
)
def hermes_rotation_status() -> dict[str, Any]:
    """Check LLM rotation configuration and health.

    Returns:
        dict with keys: status, rotation_models, active_cooldowns
    """
    try:
        client = _get_client()
        router = client._router
        models = router.get_rotation_models()
        import time

        now = time.time()
        cooldowns = {
            m_id: f"{int(expiry - now)}s remaining"
            for m_id, expiry in router._cooldowns.items()
            if expiry > now
        }
        return {
            "status": "success",
            "rotation_models": models,
            "active_cooldowns": cooldowns,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Merge multiple source sessions into a destination session. "
        "Useful for consolidating research or combining context from parallel tasks."
    ),
)
def hermes_session_merge(
    target_id: str,
    source_ids: list[str],
    deduplicate: bool = True,
) -> dict[str, Any]:
    """Consolidate multiple sessions into one.

    Args:
        target_id: Destination session ID (created if missing).
        source_ids: List of session IDs to pull messages from.
        deduplicate: Skip exact back-to-back duplicates (default True).

    Returns:
        dict with status, message
    """
    try:
        client = _get_client()
        ok = client.session_merge(target_id, source_ids, deduplicate=deduplicate)
        return {
            "status": "success" if ok else "error",
            "message": f"Merged sources into {target_id}" if ok else "Merge failed or no sessions found",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Perform a comprehensive health check of the Hermes agent subsystem. "
        "Verifies CLI binary, Ollama backend, API keys, and session database integrity."
    ),
)
def hermes_health_check() -> dict[str, Any]:
    """Deep diagnostic check for Hermes.

    Returns:
        dict with diagnostic report
    """
    try:
        client = _get_client()
        status = client.get_hermes_status()
        
        # Check sessions DB
        from codomyrmex.agents.hermes.session import SQLiteSessionStore
        with SQLiteSessionStore(client._session_db_path) as store:
            db_stats = store.get_stats()
            
        # Check rotation models
        models = client._router.get_rotation_models()
        
        return {
            "status": "success",
            "backends": status,
            "database": db_stats,
            "rotation_config": {
                "active_models": len(models),
                "path": client._router._rotation_path,
            },
            "environment": {
                "python_version": sys.version.split()[0],
                "platform": sys.platform,
            }
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

