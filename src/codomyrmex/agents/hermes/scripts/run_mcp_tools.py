"""MCP tools direct exercise script.

Calls the three Hermes MCP tool functions directly and validates
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
)


def run_mcp_tools(
    *,
    prompt: str = "Say hello in one sentence.",
) -> dict[str, Any]:
    """Call all Hermes MCP tools and return consolidated results.

    Args:
        prompt: Prompt to send via ``hermes_execute``.

    Returns:
        Dict with results from ``hermes_status``, ``hermes_execute``,
        and ``hermes_skills_list``.
    """
    start = time.time()
    results: dict[str, Any] = {}

    # ── 1. hermes_status ─────────────────────────────────────────────
    status = hermes_status()
    results["status_tool"] = {
        "status": status.get("status"),
        "available": status.get("available"),
        "active_backend": status.get("active_backend"),
        "has_status_key": "status" in status,
    }

    # ── 2. hermes_execute ────────────────────────────────────────────
    execute_result = hermes_execute(prompt=prompt)
    results["execute_tool"] = {
        "status": execute_result.get("status"),
        "has_content": bool(execute_result.get("content")),
        "has_metadata": "metadata" in execute_result,
        "content_length": len(execute_result.get("content", "")),
    }

    # ── 3. hermes_skills_list ────────────────────────────────────────
    skills_result = hermes_skills_list()
    results["skills_tool"] = {
        "status": skills_result.get("status"),
        "has_output_or_message": "output" in skills_result
        or "message" in skills_result,
    }

    # ── Summary ──────────────────────────────────────────────────────
    elapsed = time.time() - start
    results["total_elapsed_s"] = round(elapsed, 3)
    results["all_have_status_key"] = all(
        "status" in results[k] for k in ["status_tool", "execute_tool", "skills_tool"]
    )

    return results


def main() -> None:
    """CLI entry point."""
    prompt = (
        " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Say hello in one sentence."
    )
    result = run_mcp_tools(prompt=prompt)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
