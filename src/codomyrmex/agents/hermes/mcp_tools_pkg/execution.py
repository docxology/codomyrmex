"""Hermes MCP tools — execution category."""
from __future__ import annotations

from typing import Any

from codomyrmex.agents.hermes.mcp_tools_pkg._client import _get_client
from codomyrmex.agents.hermes.skill_names import agent_context_for_hermes_skills
from codomyrmex.model_context_protocol.decorators import mcp_tool


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
        prompts: list of prompt strings to process.
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

    Uses a Hermes-local dispatcher with the provided *capability_profile*,
    registers the built-in Hermes client under the requested role, then runs the
    best matching callable.

    Args:
        role: Capability role name (e.g. ``"code_reviewer"``, ``"summariser"``).
        task: Natural language task description.
        capability_profile: dict mapping role → list of allowed agent name prefixes.
            Defaults to ``{role: [role]}`` if omitted.

    Returns:
        dict with status, role, agent, result (or error).
    """
    try:
        from codomyrmex.agents.hermes._dispatch import spawn_agent

        profile = capability_profile or {role: [role]}

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

        return spawn_agent(
            role,
            task,
            agents={role: _hermes_agent},
            capability_profile=profile,
        )
    except Exception as exc:
        return {"status": "error", "role": role, "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "set or replace the persistent system prompt for a Hermes session. "
        "The system prompt is always the first message and guides agent behaviour."
    ),
)
def hermes_set_system_prompt(
    session_id: str,
    prompt: str,
) -> dict[str, Any]:
    """set the system prompt for a Hermes session.

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
