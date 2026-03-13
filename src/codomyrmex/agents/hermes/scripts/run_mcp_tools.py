"""MCP tools direct exercise script.

Calls all six Hermes MCP tool functions directly and validates
their return structures.

Usage::

    python -m codomyrmex.agents.hermes.scripts.run_mcp_tools
"""

from __future__ import annotations

import json
import sys
import time
from typing import Any

from codomyrmex.agents.hermes.mcp_tools import (
    hermes_execute,
    hermes_skills_list,
    hermes_status,
    hermes_stream,
    hermes_template_list,
    hermes_template_render,
)


def _probe_core(prompt: str) -> dict[str, Any]:
    """Probe status, execute, and skills tools."""
    status = hermes_status()
    execute = hermes_execute(prompt=prompt)
    skills = hermes_skills_list()
    return {
        "status_tool": {
            "status": status.get("status"),
            "available": status.get("available"),
            "active_backend": status.get("active_backend"),
        },
        "execute_tool": {
            "status": execute.get("status"),
            "has_content": bool(execute.get("content")),
            "content_length": len(execute.get("content", "")),
        },
        "skills_tool": {
            "status": skills.get("status"),
            "has_output_or_message": "output" in skills or "message" in skills,
        },
    }


def _probe_templates(prompt: str) -> dict[str, Any]:
    """Probe template_list, template_render, and stream tools."""
    tpl_list = hermes_template_list()
    tpl_render = hermes_template_render(
        template_name="code_review",
        variables={"language": "python", "code": "x = 1", "focus_areas": "all"},
    )
    stream = hermes_stream(prompt=prompt, timeout=5)
    return {
        "template_list_tool": {
            "status": tpl_list.get("status"),
            "count": tpl_list.get("count", 0),
        },
        "template_render_tool": {
            "status": tpl_render.get("status"),
            "has_rendered_prompt": bool(tpl_render.get("rendered_prompt")),
            "has_system_prompt": bool(tpl_render.get("system_prompt")),
        },
        "stream_tool": {
            "status": stream.get("status"),
            "has_lines": "lines" in stream,
        },
    }


def run_mcp_tools(*, prompt: str = "Say hello in one sentence.") -> dict[str, Any]:
    """Call all Hermes MCP tools and return consolidated results.

    Args:
        prompt: Prompt forwarded to ``hermes_execute`` and ``hermes_stream``.

    Returns:
        Dict with per-tool results, ``total_elapsed_s``, and ``all_have_status_key``.
    """
    start = time.time()
    results: dict[str, Any] = {**_probe_core(prompt), **_probe_templates(prompt)}
    results["total_elapsed_s"] = round(time.time() - start, 3)
    results["all_have_status_key"] = all(
        "status" in results[k] for k in results if k.endswith("_tool")
    )
    return results


def main() -> None:
    """CLI entry point."""
    prompt = (
        " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Say hello in one sentence."
    )
    print(json.dumps(run_mcp_tools(prompt=prompt), indent=2, default=str))


if __name__ == "__main__":
    main()
