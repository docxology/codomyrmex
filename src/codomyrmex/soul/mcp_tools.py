"""MCP tools for the soul module.

Exposes five stateless tools that create a fresh SoulAgent per call.
Persistent state lives in SOUL.md and MEMORY.md — not in Python objects.

Tools:
    soul_ask    — Ask a persistent agent a question.
    soul_remember — Manually append a note to MEMORY.md.
    soul_reset  — Clear in-session conversation history.
    soul_status — Return file statistics for SOUL.md + MEMORY.md.
    soul_init   — Create default SOUL.md + MEMORY.md for a new agent.
"""

from __future__ import annotations

import os
from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .agent import HAS_SOUL, SoulAgent
from .exceptions import SoulError


def _import_guard() -> dict[str, Any] | None:
    """Return an error dict when soul-agent is not installed, else None."""
    if not HAS_SOUL:
        return {
            "status": "error",
            "message": "soul-agent is not installed. Run: uv sync --extra soul",
        }
    return None


@mcp_tool(category="soul")
def soul_ask(
    question: str,
    soul_path: str = "SOUL.md",
    memory_path: str = "MEMORY.md",
    provider: str = "anthropic",
    model: str | None = None,
    base_url: str | None = None,
    remember: bool = True,
) -> dict[str, Any]:
    """Ask a persistent markdown-memory agent a question.

    The agent reads its identity from SOUL.md and its conversation history
    from MEMORY.md.  When ``remember`` is True the exchange is appended to
    MEMORY.md so future calls can reference it.

    Args:
        question: Question or statement to send to the agent.
        soul_path: Path to SOUL.md (agent identity). Default: SOUL.md.
        memory_path: Path to MEMORY.md (conversation log). Default: MEMORY.md.
        provider: LLM provider — 'anthropic', 'openai', or 'openai-compatible'.
        model: Model name override (uses provider default when omitted).
        base_url: Base URL for openai-compatible endpoints (e.g. Ollama).
        remember: When True, persist the exchange to MEMORY.md.

    Returns:
        {'status': 'success', 'response': str, 'remembered': bool}
        or {'status': 'error', 'message': str}
    """
    err = _import_guard()
    if err:
        return err
    try:
        agent = SoulAgent(
            soul_path=soul_path,
            memory_path=memory_path,
            provider=provider,
            model=model,
            base_url=base_url,
        )
        response = agent.ask(question, remember=remember)
        return {"status": "success", "response": response, "remembered": remember}
    except SoulError as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(category="soul")
def soul_remember(
    note: str,
    soul_path: str = "SOUL.md",
    memory_path: str = "MEMORY.md",
    provider: str = "anthropic",
) -> dict[str, Any]:
    """Manually append a note to the agent's MEMORY.md.

    Useful for injecting context (facts, decisions, preferences) that the
    agent should recall in future conversations.

    Args:
        note: Text note to append to persistent memory.
        soul_path: Path to SOUL.md.
        memory_path: Path to MEMORY.md.
        provider: LLM provider (required for SoulAgent construction).

    Returns:
        {'status': 'success', 'memory_path': str}
        or {'status': 'error', 'message': str}
    """
    err = _import_guard()
    if err:
        return err
    try:
        agent = SoulAgent(
            soul_path=soul_path,
            memory_path=memory_path,
            provider=provider,
        )
        agent.remember(note)
        return {"status": "success", "memory_path": memory_path}
    except SoulError as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(category="soul")
def soul_reset(
    soul_path: str = "SOUL.md",
    memory_path: str = "MEMORY.md",
    provider: str = "anthropic",
) -> dict[str, Any]:
    """Reset in-session conversation history without modifying MEMORY.md.

    Use this to start a fresh conversation context while keeping the
    agent's long-term persistent memory intact.

    Args:
        soul_path: Path to SOUL.md.
        memory_path: Path to MEMORY.md.
        provider: LLM provider.

    Returns:
        {'status': 'success', 'note': str}
        or {'status': 'error', 'message': str}
    """
    err = _import_guard()
    if err:
        return err
    try:
        agent = SoulAgent(
            soul_path=soul_path,
            memory_path=memory_path,
            provider=provider,
        )
        agent.reset_conversation()
        return {
            "status": "success",
            "note": "In-session history cleared. MEMORY.md is unchanged.",
        }
    except SoulError as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(category="soul")
def soul_status(
    soul_path: str = "SOUL.md",
    memory_path: str = "MEMORY.md",
) -> dict[str, Any]:
    """Return file statistics for SOUL.md and MEMORY.md.

    Does not require soul-agent to be installed — operates on file metadata only.

    Args:
        soul_path: Path to SOUL.md.
        memory_path: Path to MEMORY.md.

    Returns:
        Dictionary with status, paths, and per-file exists/size_bytes keys.
    """
    result: dict[str, Any] = {
        "status": "success",
        "soul_path": soul_path,
        "memory_path": memory_path,
    }
    for key, path in [("soul", soul_path), ("memory", memory_path)]:
        if os.path.exists(path):
            result[f"{key}_exists"] = True
            result[f"{key}_size_bytes"] = os.path.getsize(path)
        else:
            result[f"{key}_exists"] = False
            result[f"{key}_size_bytes"] = 0
    return result


@mcp_tool(category="soul")
def soul_init(
    soul_path: str = "SOUL.md",
    memory_path: str = "MEMORY.md",
    agent_name: str = "Assistant",
    description: str = "A helpful AI assistant with persistent memory.",
) -> dict[str, Any]:
    """Create default SOUL.md and MEMORY.md for a new agent.

    Existing files are NOT overwritten — only missing files are created.
    Does not require soul-agent to be installed.

    Args:
        soul_path: Destination path for SOUL.md.
        memory_path: Destination path for MEMORY.md.
        agent_name: Agent name embedded in the SOUL.md header.
        description: Agent description / system prompt content.

    Returns:
        {'status': 'success', 'created': [paths], 'skipped': [paths]}
        or {'status': 'error', 'message': str}
    """
    created: list[str] = []

    if not os.path.exists(soul_path):
        soul_content = (
            f"# {agent_name}\n\n"
            f"{description}\n\n"
            "## Personality\n\n"
            "Be concise, helpful, and remember past context.\n"
        )
        try:
            with open(soul_path, "w", encoding="utf-8") as fh:
                fh.write(soul_content)
            created.append(soul_path)
        except OSError as exc:
            return {"status": "error", "message": f"Cannot write {soul_path}: {exc}"}

    if not os.path.exists(memory_path):
        try:
            with open(memory_path, "w", encoding="utf-8") as fh:
                fh.write("# Memory Log\n\n")
            created.append(memory_path)
        except OSError as exc:
            return {"status": "error", "message": f"Cannot write {memory_path}: {exc}"}

    skipped = [p for p in [soul_path, memory_path] if p not in created]
    return {"status": "success", "created": created, "skipped": skipped}
