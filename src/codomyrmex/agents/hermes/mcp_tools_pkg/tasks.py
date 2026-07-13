"""Hermes MCP tools — tasks category."""
from __future__ import annotations

from typing import Any

from codomyrmex.agents.hermes.mcp_tools_pkg._client import _get_client
from codomyrmex.model_context_protocol.decorators import mcp_tool


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
        use_regex: set to True to treat the query as a regular expression.

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
