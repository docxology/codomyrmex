"""Streaming Hermes chat execution.

Exercises ``HermesClient.stream()`` to yield output lines in real time.

Usage::

    python -m codomyrmex.agents.hermes.scripts.run_stream "List 3 Python tips"
"""

from __future__ import annotations

import sys
import time
from typing import Any

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes.hermes_client import HermesClient, HermesError


def run_stream(
    prompt: str,
    *,
    backend: str = "auto",
    model: str = "hermes3",
    timeout: int = 120,
) -> dict[str, Any]:
    """Stream a prompt and collect all output lines.

    Args:
        prompt: Natural-language prompt.
        backend: Backend preference.
        model: Ollama model name.
        timeout: Subprocess timeout in seconds.

    Returns:
        Dict with keys: ``status``, ``lines``, ``line_count``,
        ``elapsed_s``, ``backend``.
    """
    client = HermesClient(
        config={
            "hermes_backend": backend,
            "hermes_model": model,
            "hermes_timeout": timeout,
        }
    )

    lines: list[str] = []
    start = time.time()

    try:
        request = AgentRequest(prompt=prompt)
        for line in client.stream(request):
            lines.append(line)
        elapsed = time.time() - start
        return {
            "status": "success" if lines else "empty",
            "lines": lines,
            "line_count": len(lines),
            "elapsed_s": round(elapsed, 3),
            "backend": client.active_backend,
        }
    except HermesError as exc:
        elapsed = time.time() - start
        return {
            "status": "error",
            "lines": lines,
            "line_count": len(lines),
            "error": str(exc),
            "elapsed_s": round(elapsed, 3),
            "backend": client.active_backend,
        }


def main() -> None:
    """CLI entry point — pass prompt as first argument."""
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "List 3 Python tips"
    result = run_stream(prompt)
    for line in result["lines"]:
        print(line)
    print(
        f"\n--- {result['line_count']} lines in {result['elapsed_s']}s ({result['backend']}) ---"
    )
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
