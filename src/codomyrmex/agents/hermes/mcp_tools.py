"""MCP tool definitions for the Hermes agent module.

Exposes Hermes chat execution, skills management, and status as MCP tools.
Automatically uses Ollama hermes3 when the Hermes CLI is unavailable.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from codomyrmex.agents.hermes.skill_names import agent_context_for_hermes_skills
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
    tags=["hermes", "skills", "cli_preload", "interop"],
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
    hermes_skill: str | None = None,
    hermes_skills: list[str] | str | None = None,
) -> dict[str, Any]:
    """Submit a prompt to the Hermes agent.

    Args:
        prompt: Natural-language task description.
        backend: ``"auto"`` (default), ``"cli"``, or ``"ollama"``.
        model: Ollama model name (default ``hermes3``).
        timeout: Subprocess timeout in seconds (default 120).
        hermes_skill: Optional Hermes CLI skill name (``hermes chat -s``). Ollama ignores.
        hermes_skills: Optional list or comma-separated skill names for CLI preload.

    Returns:
        dict with keys: status, content, error, metadata

    """
    try:
        from codomyrmex.agents.core import AgentRequest

        client = _get_client(backend=backend, model=model, timeout=timeout)
        ctx = agent_context_for_hermes_skills(hermes_skill, hermes_skills)
        request = AgentRequest(prompt=prompt, context=ctx)
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
    tags=["hermes", "skills", "registry", "interop"],
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
    tags=["hermes", "skills", "registry", "interop"],
    description=(
        "Resolve registry skill_ids to Hermes CLI -s names and metadata. "
        "Uses bundled registry plus optional CODOMYRMEX_SKILLS_REGISTRY overlay."
    ),
)
def hermes_skills_resolve(skill_ids: list[str] | str) -> dict[str, Any]:
    """Map stable registry ids to Hermes preload names for MCP / PAI routing."""
    try:
        from codomyrmex.agents.hermes import skill_registry

        resolved = skill_registry.resolve_skill_ids(skill_ids)
        return {"status": "success", **resolved}
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "skill_ids_requested": [],
            "unknown_skill_ids": [],
            "hermes_preload": [],
            "resolved_entries": [],
        }


@mcp_tool(
    category="hermes",
    tags=["hermes", "skills", "registry", "interop"],
    description=(
        "Validate registry hermes_preload names against Hermes CLI skills list when available."
    ),
)
def hermes_skills_validate_registry() -> dict[str, Any]:
    """Structural + optional live check against ``hermes skills list``."""
    try:
        from codomyrmex.agents.hermes import skill_registry

        idx = skill_registry.load_skill_index()
        base: dict[str, Any] = {
            "registry_skill_count": len(idx),
            "skill_ids": sorted(idx.keys()),
        }
        client = _get_client(timeout=30)
        if client.active_backend != "cli":
            return {
                **base,
                "status": "skipped",
                "reason": "Hermes CLI backend required for live list comparison",
            }
        res = client.list_skills()
        if not res.get("success"):
            return {
                **base,
                "status": "error",
                "message": res.get("error", "list_skills failed"),
            }
        out = res.get("output") or ""
        val = skill_registry.validate_registry_against_cli_lines(out, index=idx)
        return {"status": val.get("status", "ok"), **base, **val}
    except Exception as exc:
        return {"status": "error", "message": str(exc), "registry_skill_count": 0}


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
    tags=["hermes", "skills", "cli_preload", "interop"],
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
    hermes_skill: str | None = None,
    hermes_skills: list[str] | str | None = None,
) -> dict[str, Any]:
    """Stream Hermes agent output and collect all lines.

    Args:
        prompt: Natural-language task description.
        backend: ``"auto"`` (default), ``"cli"``, or ``"ollama"``.
        model: Ollama model name (default ``hermes3``).
        timeout: Subprocess timeout in seconds (default 120).
        hermes_skill: Optional Hermes CLI skill for preload on stream (CLI only).
        hermes_skills: Optional skill list or comma-separated string (CLI only).

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
        ctx = agent_context_for_hermes_skills(hermes_skill, hermes_skills)
        request = AgentRequest(prompt=prompt, context=ctx)
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
    tags=["hermes", "skills", "cli_preload", "interop"],
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
    hermes_skill: str | None = None,
    hermes_skills: list[str] | str | None = None,
) -> dict[str, Any]:
    """Submit a prompt to a stateful Hermes agent session.

    Args:
        prompt: Natural-language task description.
        session_id: Session ID to continue, or None to start a new one.
        backend: ``"auto"`` (default), ``"cli"``, or ``"ollama"``.
        model: Ollama model name (default ``hermes3``).
        timeout: Subprocess timeout in seconds (default 120).
        hermes_skill: Optional Hermes CLI skill; persisted on the session for later turns.
        hermes_skills: Optional skill list or comma-separated string (same persistence).

    Returns:
        dict with keys: status, content, session_id, error, metadata

    """
    try:
        client = _get_client(backend=backend, model=model, timeout=timeout)
        response = client.chat_session(
            prompt=prompt,
            session_id=session_id,
            hermes_skill=hermes_skill,
            hermes_skills=hermes_skills,
        )
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
    tags=["hermes", "skills", "cli_preload", "interop"],
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
    hermes_skill: str | None = None,
    hermes_skills: list[str] | str | None = None,
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
        hermes_skill: Optional Hermes CLI skill preload.
        hermes_skills: Optional skill list or comma-separated string.

    Returns:
        dict with keys: status, content, model, stop_reason, usage

    """
    try:
        from codomyrmex.agents.core import AgentRequest

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        client = _get_client(backend=backend, model=model, timeout=120)
        ctx = agent_context_for_hermes_skills(hermes_skill, hermes_skills)
        request = AgentRequest(prompt=full_prompt, context=ctx)
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
        if parent_cid and request.metadata is not None:
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
    tags=["hermes", "skills", "cli_preload", "interop"],
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
    hermes_skill: str | None = None,
    hermes_skills: list[str] | str | None = None,
) -> dict[str, Any]:
    """Execute a batch of prompts with the Hermes agent.

    Args:
        prompts: List of prompt strings to process.
        parallel: Submit all prompts concurrently (default False).
        backend: ``"auto"`` (default), ``"cli"``, or ``"ollama"``.
        timeout: Per-prompt timeout in seconds (default 120).
        hermes_skill: Optional Hermes CLI skill applied to each prompt.
        hermes_skills: Optional skill list or comma-separated string for each prompt.

    Returns:
        dict with keys: status, results (list of {prompt, status, content, error}), count

    """
    try:
        client = _get_client(backend=backend, timeout=timeout)
        results = client.batch_execute(
            prompts,
            parallel=parallel,
            hermes_skill=hermes_skill,
            hermes_skills=hermes_skills,
        )
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
            "message": f"Merged sources into {target_id}"
            if ok
            else "Merge failed or no sessions found",
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
            },
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


# ── v1.3.0: Graph Link Inference ─────────────────────────────────────


@mcp_tool(
    category="hermes",
    description=(
        "Extract bi-directional [[Concept Link]] references from all Hermes sessions "
        "and return a lightweight knowledge graph of nodes and edges. "
        "Use this to see how topics connect across the agentic memory."
    ),
)
def hermes_build_memory_graph(
    min_link_count: int = 1,
) -> dict[str, Any]:
    """Build a concept-link graph from all Hermes session messages.

    Scans every stored session for ``[[WikiLink]]``-style references and
    constructs a directed graph where nodes are concept names and edges
    represent co-occurrence within the same session.

    Args:
        min_link_count: Minimum number of sessions a concept must appear in
            to be included as a node (default 1).

    Returns:
        dict with status, nodes (list of str), edges (list of {source, target, weight}),
        and session_count.
    """
    try:
        import os
        import re
        from collections import Counter, defaultdict
        from pathlib import Path

        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        WORKSPACE_ROOT = Path(os.path.abspath(".")).resolve()
        db_path = WORKSPACE_ROOT / ".codomyrmex" / "hermes_sessions.db"

        WIKI_LINK_RE = re.compile(r"\[\[([^\[\]|#]+?)(?:[|#][^\]]+)?\]\]")

        concept_sessions: dict[str, set[str]] = defaultdict(set)
        edge_weights: Counter[tuple[str, str]] = Counter()

        with SQLiteSessionStore(db_path) as store:
            session_ids = store.list_sessions()
            for sid in session_ids:
                session = store.load(sid)
                if session is None:
                    continue
                full_text = " ".join(m.get("content", "") for m in session.messages)
                concepts_in_session = set(WIKI_LINK_RE.findall(full_text))
                for concept in concepts_in_session:
                    concept_sessions[concept].add(sid)
                # Directed edges: concept → all other concepts in same session
                for c1 in concepts_in_session:
                    for c2 in concepts_in_session:
                        if c1 != c2:
                            edge_weights[(c1, c2)] += 1

        # Filter to nodes that appear in enough sessions
        nodes = [
            c for c, sids in concept_sessions.items() if len(sids) >= min_link_count
        ]
        node_set = set(nodes)
        edges = [
            {"source": src, "target": tgt, "weight": w}
            for (src, tgt), w in edge_weights.items()
            if src in node_set and tgt in node_set
        ]

        return {
            "status": "success",
            "session_count": len(session_ids),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": sorted(nodes),
            "edges": sorted(edges, key=lambda e: -e["weight"]),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "nodes": [], "edges": []}


# ── v1.4.0: Autonomous Knowledge Codification MCP tools ─────────────


@mcp_tool(
    category="hermes",
    description=(
        "Extract a structured Knowledge Item (KI) from a Hermes session and persist it "
        "to the agentic knowledge memory. Use after complex multi-step sessions to "
        "crystallise reusable knowledge for future recall."
    ),
)
def hermes_extract_ki(
    session_id: str,
    title: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Persist a Knowledge Item derived from a Hermes session.

    Loads the session messages, concatenates the assistant turns into a body,
    and stores it via :class:`~codomyrmex.agentic_memory.memory.KnowledgeMemory`.

    Args:
        session_id: The Hermes session to extract from.
        title: Short title for the KI (auto-generated from session name if omitted).
        tags: Optional topic tags.

    Returns:
        dict with status, memory_id, title, and body_length.
    """
    try:
        import os
        from pathlib import Path

        from codomyrmex.agentic_memory.memory import KnowledgeMemory
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        WORKSPACE_ROOT = Path(os.path.abspath(".")).resolve()
        db_path = WORKSPACE_ROOT / ".codomyrmex" / "hermes_sessions.db"

        with SQLiteSessionStore(db_path) as store:
            session = store.load(session_id)

        if session is None:
            return {"status": "error", "message": f"Session '{session_id}' not found."}

        # Extract assistant outputs as the KI body
        body_parts = [
            m["content"]
            for m in session.messages
            if m.get("role") == "assistant" and m.get("content")
        ]
        body = "\n\n".join(body_parts) if body_parts else "(no assistant turns)"

        ki_title = title or (session.name or f"KI from session {session_id[:8]}")

        km = KnowledgeMemory()
        mem = km.store(
            title=ki_title,
            body=body,
            tags=tags or [],
            source_session_id=session_id,
        )

        return {
            "status": "success",
            "memory_id": mem.id,
            "title": ki_title,
            "body_length": len(body),
            "tags": tags or [],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Search stored Knowledge Items (KIs) by topic. Returns ranked results from "
        "the agentic semantic memory. Use before beginning complex tasks to check if "
        "the relevant knowledge has already been codified."
    ),
)
def hermes_search_knowledge_items(
    topic: str,
    limit: int = 5,
) -> dict[str, Any]:
    """Retrieve ranked Knowledge Items relevant to *topic*.

    Uses token-overlap relevance scoring across all SEMANTIC memories.

    Args:
        topic: Natural language search string.
        limit: Maximum number of results to return.

    Returns:
        dict with status, count, and results list containing title, body snippet, score.
    """
    try:
        from codomyrmex.agentic_memory.memory import KnowledgeMemory

        km = KnowledgeMemory()
        results = km.recall(topic, k=limit)

        items = []
        for r in results:
            meta = r.memory.metadata or {}
            items.append(
                {
                    "memory_id": r.memory.id,
                    "title": meta.get("title", "(untitled)"),
                    "snippet": r.memory.content[:200],
                    "tags": meta.get("tags", []),
                    "source_session_id": meta.get("source_session_id", ""),
                    "relevance": round(r.relevance_score, 4),
                    "combined_score": round(r.combined_score, 4),
                }
            )

        return {
            "status": "success",
            "topic": topic,
            "count": len(items),
            "results": items,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "results": []}


@mcp_tool(
    category="hermes",
    description=(
        "Merge near-duplicate Knowledge Items in the agentic memory to keep the "
        "knowledge base clean and non-redundant. Items above the similarity threshold "
        "are folded into their older counterpart as dated Update sections."
    ),
)
def hermes_deduplicate_ki(
    threshold: float = 0.85,
) -> dict[str, Any]:
    """Deduplicate Knowledge Items by merging similar entries.

    Computes token-overlap similarity between all SEMANTIC memories.
    Items with similarity ≥ *threshold* relative to an existing older item
    are merged into it (body appended as ``## Update``) and deleted.

    Args:
        threshold: Similarity threshold 0.0–1.0 (default 0.85).

    Returns:
        dict with status, merged_count, and message.
    """
    try:
        from codomyrmex.agentic_memory.memory import KnowledgeMemory

        km = KnowledgeMemory()
        merged = km.merge_duplicates(threshold=threshold)

        return {
            "status": "success",
            "merged_count": merged,
            "threshold": threshold,
            "message": f"Merged {merged} duplicate Knowledge Item(s) at threshold {threshold}.",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


# ── v1.5.0 D1: Capability-Profile Agent Spawning ─────────────────────


@mcp_tool(
    category="hermes",
    description=(
        "Dispatch a task to the most suitable registered agent for a given capability role. "
        "Uses the AgentOrchestrator capability_profile to filter agents by role, then "
        "forwards the task to the best match. Useful for dynamic multi-agent delegation."
    ),
)
def hermes_spawn_agent(
    role: str,
    task: str,
    capability_profile: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Dispatch a capability-scoped task to a matching agent.

    Instantiates an :class:`~codomyrmex.orchestrator.integration.AgentOrchestrator`
    with the provided *capability_profile*, registers the built-in Hermes client
    under the role's first allowed prefix, then calls :meth:`spawn_agent`.

    Args:
        role: Capability role name (e.g. ``"code_reviewer"``, ``"summariser"``).
        task: Natural language task description.
        capability_profile: Dict mapping role → list of allowed agent name prefixes.
            Defaults to ``{role: [role]}`` if omitted.

    Returns:
        dict with status, role, agent, result (or error).
    """
    try:
        from codomyrmex.orchestrator.integration import AgentOrchestrator

        profile = capability_profile or {role: [role]}
        orch = AgentOrchestrator(capability_profile=profile)

        # Wire a real HermesClient agent behind the requested role.
        # Falls back to a thin delegate when the hermes binary is unavailable
        # (e.g. test environments) so the MCP tool always returns a usable result.
        try:
            client = _get_client(backend="auto")

            def _hermes_agent(t: str, **_kw: Any) -> dict[str, Any]:
                """Real HermesClient delegate — runs a one-shot prompt."""
                from codomyrmex.agents.core import AgentRequest

                result = client.execute(AgentRequest(prompt=t))
                return {
                    "task": t,
                    "agent": "hermes",
                    "backend": getattr(client, "_active_backend", "auto"),
                    "result": result.content
                    if hasattr(result, "content")
                    else str(result),
                }

        except Exception:
            # HermesClient unavailable (hermes binary / Ollama not installed)
            def _hermes_agent(t: str, **_kw: Any) -> dict[str, Any]:
                return {
                    "task": t,
                    "agent": "hermes",
                    "note": "Hermes agent delegated (stub)",
                }

        orch.register_agent(role, _hermes_agent)

        return orch.spawn_agent(role, task)
    except Exception as exc:
        return {"status": "error", "role": role, "message": str(exc)}


# ── v1.3.0 D3: Size-Based Memory GC ──────────────────────────────────


@mcp_tool(
    category="hermes",
    description=(
        "Archive and prune Hermes sessions when the database exceeds a size threshold. "
        "Sessions are compressed to .json.gz files in a sessions_archive/ directory "
        "adjacent to the DB, then removed from SQLite to keep the store lean. "
        "Set dry_run=True to see what would be pruned without deleting anything."
    ),
)
def hermes_archive_sessions(
    max_size_mb: float = 50.0,
    days_old: int = 7,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Prune Hermes sessions by DB size and age, archiving to .json.gz.

    Runs GC only when ``db_size_bytes / 1_048_576 >= max_size_mb``.  Deletes
    sessions older than *days_old* days to bring the store back under threshold.

    Args:
        max_size_mb: Trigger threshold in megabytes (default 50).
        days_old: Age cutoff in days for sessions to archive (default 7).
        dry_run: If True, return stats without modifying the DB.

    Returns:
        dict with status, db_size_mb, threshold_mb, pruned_count, and
        archived_dir path.
    """
    try:
        import os
        from pathlib import Path

        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        WORKSPACE_ROOT = Path(os.path.abspath(".")).resolve()
        db_path = WORKSPACE_ROOT / ".codomyrmex" / "hermes_sessions.db"

        stats: dict[str, Any] = {
            "status": "ok",
            "threshold_mb": max_size_mb,
            "db_size_mb": 0.0,
            "pruned_count": 0,
            "archived_dir": str(db_path.parent / "sessions_archive"),
            "dry_run": dry_run,
        }

        if not db_path.exists():
            stats["message"] = "Session DB not found; nothing to archive."
            return stats

        size_bytes = os.path.getsize(db_path)
        size_mb = size_bytes / 1_048_576
        stats["db_size_mb"] = round(size_mb, 3)

        if size_mb < max_size_mb:
            stats["message"] = (
                f"DB is {size_mb:.2f} MB — under threshold {max_size_mb} MB. "
                "No pruning needed."
            )
            return stats

        if dry_run:
            # Count sessions that would be pruned without touching anything
            import sqlite3
            import time

            threshold = time.time() - (days_old * 86400)
            conn = sqlite3.connect(str(db_path))
            try:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM hermes_sessions WHERE updated_at < ?",
                    (threshold,),
                )
                would_prune = cursor.fetchone()[0]
            finally:
                conn.close()
            stats["pruned_count"] = would_prune
            stats["message"] = f"Dry run: would prune {would_prune} session(s)."
            return stats

        with SQLiteSessionStore(db_path) as store:
            pruned = store.prune_old_sessions(days_old=days_old)
            stats["pruned_count"] = pruned
            stats["message"] = (
                f"Pruned {pruned} session(s) older than {days_old} day(s). "
                f"DB was {size_mb:.2f} MB (threshold: {max_size_mb} MB)."
            )
        return stats

    except Exception as exc:
        return {"status": "error", "message": str(exc)}


# ── v0.4.0: Gateway management, model info, pairing, skill install ────


@mcp_tool(
    category="hermes",
    description=(
        "Query the status of all running Hermes gateway instances. "
        "Returns each instance name, running state, and active model (v0.4.0+)."
    ),
)
def hermes_gateway_status() -> dict[str, Any]:
    """Get live status for all Hermes gateway instances.

    Returns:
        dict with keys: status, instances (list), output
    """
    try:
        client = _get_client()
        result = client.get_gateway_status()
        return {
            "status": "success" if result.get("success") else "error",
            "instances": result.get("instances", []),
            "output": result.get("output", ""),
            "error": result.get("error", ""),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "instances": []}


@mcp_tool(
    category="hermes",
    description=(
        "Look up context length, tool-use support, and provider metadata for a "
        "given model ID. Queries the Hermes model catalog first, then falls "
        "back to the CLI (v0.4.0 model metadata expansion)."
    ),
)
def hermes_model_info(model_id: str) -> dict[str, Any]:
    """Retrieve metadata for a specific model ID.

    Args:
        model_id: OpenRouter model ID, e.g. ``"nvidia/nemotron-3-super-120b-a12b:free"``.

    Returns:
        dict with keys: status, model_id, context_length, supports_tools, provider, source
    """
    try:
        client = _get_client()
        info = client.get_model_info(model_id)
        return {"status": "success" if "error" not in info else "error", **info}
    except Exception as exc:
        return {"status": "error", "model_id": model_id, "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Send an /approve or /deny command to the Hermes gateway to confirm or "
        "cancel a pending dangerous-command approval request (v0.4.0+). "
        "Use /approve session to approve a command pattern for the entire session."
    ),
)
def hermes_approve_command(
    command: str = "/approve",
    session_id: str | None = None,
) -> dict[str, Any]:
    """Approve or deny a pending gateway command approval.

    Args:
        command: ``"/approve"``, ``"/approve session"``, or ``"/deny"``.
        session_id: Target session ID (optional).

    Returns:
        dict with keys: status, output, error
    """
    valid_commands = {"/approve", "/approve session", "/deny"}
    if command not in valid_commands:
        return {
            "status": "error",
            "message": f"Invalid command '{command}'. Use one of: {valid_commands}",
        }
    try:
        client = _get_client()
        result = client.send_gateway_command(command, session_id=session_id)
        return {
            "status": "success" if result.get("success") else "error",
            "output": result.get("output", ""),
            "error": result.get("error", ""),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "List all paired (approved) users and groups for the Hermes gateway. "
        "Reads $HERMES_HOME/pairing/telegram-approved.json."
    ),
)
def hermes_pairing_list() -> dict[str, Any]:
    """List all approved gateway users and groups.

    Returns:
        dict with keys: status, approved (dict), count
    """
    try:
        import json
        import os
        from pathlib import Path

        hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
        approved_path = hermes_home / "pairing" / "telegram-approved.json"
        if not approved_path.exists():
            return {
                "status": "success",
                "approved": {},
                "count": 0,
                "message": f"No pairing file found at {approved_path}",
            }
        approved = json.loads(approved_path.read_text())
        total = sum(len(v) if isinstance(v, list) else 1 for v in approved.values())
        return {
            "status": "success",
            "approved": approved,
            "count": total,
            "path": str(approved_path),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "approved": {}}


@mcp_tool(
    category="hermes",
    description=(
        "Add a user or group ID to the Hermes gateway pairing approved list "
        "($HERMES_HOME/pairing/telegram-approved.json). "
        "Use platform='telegram' and a numeric Telegram user/chat ID."
    ),
)
def hermes_pairing_add(
    user_id: str,
    platform: str = "telegram",
) -> dict[str, Any]:
    """Add a user or group to the gateway pairing list.

    Args:
        user_id: Numeric user or chat ID to approve.
        platform: Platform name (default ``"telegram"``).

    Returns:
        dict with keys: status, message, approved_count
    """
    try:
        import json
        import os
        from pathlib import Path

        hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
        pairing_dir = hermes_home / "pairing"
        pairing_dir.mkdir(parents=True, exist_ok=True)
        approved_path = pairing_dir / "telegram-approved.json"

        approved: dict[str, list[str]] = {}
        if approved_path.exists():
            approved = json.loads(approved_path.read_text())

        if platform not in approved:
            approved[platform] = []

        if user_id in approved[platform]:
            return {
                "status": "success",
                "message": f"{user_id} already in {platform} approved list",
                "approved_count": len(approved[platform]),
            }

        approved[platform].append(user_id)
        approved_path.write_text(json.dumps(approved, indent=2))

        return {
            "status": "success",
            "message": f"Added {user_id} to {platform} approved list",
            "approved_count": len(approved[platform]),
            "path": str(approved_path),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Install a Hermes skill from a git repository URL. "
        "Runs hermes skills install <repo_url>. "
        "Restart the gateway after installation for the skill to be available."
    ),
)
def hermes_skill_install(repo_url: str) -> dict[str, Any]:
    """Install a Hermes skill from a git URL.

    Args:
        repo_url: Git URL of the skill repository, e.g.
            ``"https://github.com/nativ3ai/hermes-geopolitical-market-sim.git"``.

    Returns:
        dict with keys: status, output, error
    """
    try:
        client = _get_client()
        result = client.install_skill(repo_url)
        return {
            "status": "success" if result.get("success") else "error",
            "output": result.get("output", ""),
            "error": result.get("error", ""),
            "tip": "Run hermes gateway restart to activate the new skill.",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    tags=["hermes", "mcp", "fastmcp", "interop"],
    description=(
        "Generate a FastMCP server scaffold for Codomyrmex↔Hermes integration. "
        "Wraps optional-skills/mcp/fastmcp/scaffold_fastmcp.py."
    ),
)
def hermes_fastmcp_scaffold(
    output_dir: str,
    server_name: str,
    force: bool = False,
) -> dict[str, Any]:
    """Scaffold a FastMCP server package via Hermes optional-skills."""
    try:
        import json

        client = _get_client()
        result = client.scaffold_fastmcp(
            output_dir=output_dir,
            server_name=server_name,
            force=force,
        )
        response: dict[str, Any] = {
            "status": "success" if result.get("success") else "error",
            "output": result.get("output", ""),
            "error": result.get("error", ""),
            "script_path": result.get("script_path", ""),
        }
        output = result.get("output", "").strip()
        if output.startswith("{") and output.endswith("}"):
            try:
                payload = json.loads(output)
                if isinstance(payload, dict):
                    response["scaffold"] = payload
            except json.JSONDecodeError:
                pass
        return response
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
