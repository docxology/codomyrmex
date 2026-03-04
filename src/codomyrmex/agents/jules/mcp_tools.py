"""MCP tool definitions for the Jules coding agent module.

Exposes Jules CLI parallel code editing and swarm dispatch as MCP tools.
All tools lazy-import JulesClient to avoid circular dependencies at collection time.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_client(command: str = "jules", timeout: int = 30) -> Any:
    """Lazy import of JulesClient to avoid circular deps."""
    from codomyrmex.agents.jules.jules_client import JulesClient

    return JulesClient(config={"jules_command": command, "jules_timeout": timeout})


@mcp_tool(
    category="jules",
    description=(
        "Check if the Jules CLI is installed and return its availability status. "
        "Returns help text when available."
    ),
)
def jules_help() -> dict[str, Any]:
    """Check Jules CLI installation status and return help information.

    Returns:
        dict with keys: status, available, help_text, error (on failure)
    """
    try:
        client = _get_client()
        info = client.get_jules_help()
        return {"status": "success", **info}
    except Exception as exc:
        return {"status": "error", "available": False, "message": str(exc)}


@mcp_tool(
    category="jules",
    description=(
        "Execute a Jules coding task against a GitHub repository. "
        "Jules autonomously writes, edits, and tests code based on the prompt."
    ),
)
def jules_execute(
    prompt: str,
    repo: str,
    parallel: int = 1,
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a coding task to Jules CLI.

    Args:
        prompt: Natural-language task description (e.g. 'add type hints to auth.py').
        repo: GitHub repository slug or local path (e.g. 'owner/repo').
        parallel: Number of Jules agents to run in parallel (default 1).
        timeout: Subprocess timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, error, metadata
    """
    try:
        from codomyrmex.agents.core import AgentRequest
        from codomyrmex.agents.jules.jules_client import JulesClient

        client = JulesClient(config={"jules_timeout": timeout})
        request = AgentRequest(
            prompt=prompt,
            context={"repo": repo, "parallel": parallel},
        )
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
    category="jules",
    description=(
        "Dispatch a parallel Jules swarm to execute all open TODO items from a "
        "TODO.md file. Parses unchecked '- [ ]' items and batches them into "
        "Jules parallel invocations."
    ),
)
def jules_dispatch_swarm(
    todo_path: str,
    repo: str,
    parallel: int = 100,
    batch_size: int = 10,
    priority_filter: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Parse a TODO.md and dispatch a Jules swarm for all open items.

    Args:
        todo_path: Absolute path to the TODO.md file to parse.
        repo: GitHub repository slug or local path (e.g. 'owner/repo').
        parallel: Jules ``--parallel`` value per batch (default 100).
        batch_size: Tasks per Jules invocation (default 10).
        priority_filter: Filter to a priority section keyword, e.g. ``"CRITICAL"``
            or ``"HIGH"``. Empty string means all open items.
        dry_run: If True, parse and return tasks without calling Jules.

    Returns:
        dict with keys: status, task_count, tasks (on dry_run),
        batch_count, responses (list of per-batch status dicts)
    """
    try:
        from codomyrmex.agents.jules.jules_client import (
            JulesClient,
            JulesSwarmDispatcher,
        )

        path = Path(todo_path)
        if not path.exists():
            return {"status": "error", "message": f"TODO file not found: {todo_path}"}

        client = JulesClient()
        dispatcher = JulesSwarmDispatcher.from_todo_md(
            client=client,
            repo=repo,
            todo_path=path,
            priority_filter=priority_filter or None,
        )

        task_count = len(dispatcher.tasks)
        batch_count = (task_count + batch_size - 1) // batch_size if task_count else 0

        if dry_run:
            return {
                "status": "success",
                "dry_run": True,
                "task_count": task_count,
                "batch_count": batch_count,
                "tasks": dispatcher.tasks,
            }

        responses = dispatcher.dispatch(parallel=parallel, batch_size=batch_size)

        return {
            "status": "success",
            "dry_run": False,
            "task_count": task_count,
            "batch_count": len(responses),
            "responses": [
                {
                    "success": r.is_success(),
                    "error": r.error,
                    "content_length": len(r.content),
                }
                for r in responses
            ],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
