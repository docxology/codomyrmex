#!/usr/bin/env python3
"""Hermes Agent — Thin Script Orchestrator.

Sends a real prompt to the Hermes agent and prints the response.
Uses Ollama hermes3 as a fallback when the Hermes CLI is unavailable.

Usage:
    python scripts/agents/hermes/run_hermes.py
    python scripts/agents/hermes/run_hermes.py "What is the capital of France?"
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_info("═" * 60)
    print_info("  Hermes Agent — Real Execution")
    print_info("═" * 60)

    try:
        from codomyrmex.agents.core import AgentRequest
        from codomyrmex.agents.hermes import HermesClient, HermesError
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    # Instantiate client (auto-detects backend)
    client = HermesClient()
    print_info(f"  Backend:   {client.active_backend}")
    print_info(f"  Model:     {client.ollama_model}")
    print_info(f"  CLI found: {client._cli_available}")
    print_info(f"  Ollama:    {client._ollama_available}")

    if client.active_backend == "none":
        print_error("No backend available. Install 'hermes' CLI or 'ollama'.")
        return 1

    # Status check
    status = client.get_hermes_status()
    print_info(f"  Status:    {status}")
    print_info("")

    # Real prompt
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Explain what Hermes Agent is in one sentence."
    print_info(f"  Prompt: {prompt}")
    print_info("─" * 60)

    try:
        request = AgentRequest(prompt=prompt)
        response = client.execute(request)

        if response.is_success():
            print_success("  Response:")
            for line in response.content.split("\n"):
                print(f"    {line}")
            print_info("")
            print_info(f"  Execution time: {response.execution_time:.2f}s")
            print_info(f"  Backend used:   {response.metadata.get('backend', 'N/A')}")
            print_info(f"  Model:          {response.metadata.get('model', 'N/A')}")
        else:
            print_error(f"  Error: {response.error}")
            return 1
    except HermesError as e:
        print_error(f"  HermesError: {e}")
        return 1

    print_info("─" * 60)
    print_success("Hermes agent execution complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
