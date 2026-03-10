"""Single-turn Hermes chat execution.

Sends a prompt through ``HermesClient.execute()`` and returns structured output.

Usage::

    python -m codomyrmex.agents.hermes.scripts.run_chat "Explain active inference"
"""

from __future__ import annotations

import json
import sys
import time
from typing import Any

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes.hermes_client import HermesClient, HermesError


def run_chat(
    prompt: str,
    *,
    backend: str = "auto",
    model: str = "hermes3",
    timeout: int = 120,
) -> dict[str, Any]:
    """Execute a single-turn chat and return structured result.

    Args:
        prompt: Natural-language prompt to send.
        backend: Backend preference.
        model: Ollama model name.
        timeout: Subprocess timeout in seconds.

    Returns:
        Dict with keys: ``status``, ``content``, ``error``,
        ``metadata``, ``elapsed_s``.
    """
    client = HermesClient(
        config={
            "hermes_backend": backend,
            "hermes_model": model,
            "hermes_timeout": timeout,
        }
    )

    start = time.time()
    try:
        request = AgentRequest(prompt=prompt)
        response = client.execute(request)
        elapsed = time.time() - start
        return {
            "status": "success" if response.is_success() else "error",
            "content": response.content,
            "error": response.error,
            "metadata": response.metadata,
            "elapsed_s": round(elapsed, 3),
            "backend": client.active_backend,
        }
    except HermesError as exc:
        elapsed = time.time() - start
        return {
            "status": "error",
            "content": "",
            "error": str(exc),
            "metadata": {},
            "elapsed_s": round(elapsed, 3),
            "backend": client.active_backend,
        }


def main() -> None:
    """CLI entry point — pass prompt as first argument."""
    prompt = (
        " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Say hello in one sentence."
    )
    result = run_chat(prompt)
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
