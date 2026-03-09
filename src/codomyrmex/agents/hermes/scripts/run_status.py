"""Hermes backend diagnostic script.

Probes CLI and Ollama availability, reports active backend and model info.

Usage::

    python -m codomyrmex.agents.hermes.scripts.run_status
"""

from __future__ import annotations

import json
import sys
from typing import Any

from codomyrmex.agents.hermes.hermes_client import HermesClient


def run_status(*, backend: str = "auto", model: str = "hermes3") -> dict[str, Any]:
    """Probe Hermes backends and return a diagnostic dict.

    Args:
        backend: Backend preference (``"auto"``, ``"cli"``, ``"ollama"``).
        model: Ollama model name.

    Returns:
        Dict with keys: ``active_backend``, ``cli_available``,
        ``ollama_available``, ``ollama_model``, ``success``.
    """
    client = HermesClient(config={
        "hermes_backend": backend,
        "hermes_model": model,
    })
    status = client.get_hermes_status()
    return {
        "active_backend": client.active_backend,
        "cli_available": status.get("cli_available", False),
        "ollama_available": status.get("ollama_available", False),
        "ollama_model": client.ollama_model,
        "success": status.get("success", False),
        "details": status,
    }


def main() -> None:
    """CLI entry point."""
    result = run_status()
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
