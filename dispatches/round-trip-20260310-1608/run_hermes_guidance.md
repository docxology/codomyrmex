# Hermes Improvement Guidance: `run_hermes.py`

_Generated: 2026-03-10T16:34:06.064442_

```python
Here is the improved Python script:

```python
#!/usr/bin/env python3
"""Hermes Agent — Thin Script Orchestrator.

Sends a real prompt to the Hermes agent and prints the response.
Uses Ollama hermes3 as a fallback when the Hermes CLI is unavailable.

Usage:
    python scripts/agents/hermes/run_hermes.py
    python scripts/agents/hermes/run_hermes.py --prompt "What is the capital of France?"
    python scripts/agents/hermes/run_hermes.py --prompt "Explain recursion" --session my-session-1
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Import required classes
from codomyrmex.agents.core.config import get_config
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)

# Define module-level constants
_DEFAULT_PROMPT = "Explain what Hermes Agent is in one sentence."
_DEFAULT_SESSION: Optional[str] = None


def _resolve_config() -> dict:
    """Load agent config and extract Hermes-specific settings.

    Returns:
        Flat dict of effective hermes config values.
    """
    try:
        config = get_config()
        hermes_cfg: dict = config.get("hermes", {}) if isinstance(config, dict) else {}
    except Exception:
        hermes_cfg = {}
    return hermes_cfg


def _load_hermes_client() -> Optional[object]:
    """Safely import and return a HermesClient instance.

    Decouples the HermesClient import from main() so it can be tested
    independently and swapped without touching orchestration logic.

    Returns:
        A HermesClient instance, or None if import fails.
    """
    try:
        from codomyrmex.agents.hermes import HermesClient
        return HermesClient()
    except ImportError as e:
        print_error(f"Import failed — cannot load HermesClient: {e}")
        return None


def _print_client_info(hermes_client: object) -> None:
    """Log infrastructure-level metadata about the initialized client.

    Args:
        hermes_client: An initialized HermesClient instance.
    """
    print_info("─" * 60)
    print_info(f"  Backend:   {hermes_client.active_backend}")  # type: ignore[attr-defined]
    print_info(f"  Model:     {hermes_client.ollama_model}")  # type: ignore[attr-defined]
    print_info(f"  CLI found: {hermes_client._cli_available}")  # type: ignore[attr-defined]
    print_info(f"  Ollama:    {hermes_client._ollama_available}")  # type: ignore[attr-defined]
    print_info(f"  DB Path:   {hermes_client._session_db_path}")  # type: ignore[attr-defined]
    try:
        status: dict = hermes_client.get_hermes_status()  # type: ignore[attr-defined]
        print_info(f"  Status:    {status}")
    except Exception as exc:
        print_info(f"  Status:    (unavailable — {exc})")


def _format_response(response: object) -> int:
    """Render a successful Hermes response to stdout via cli_helpers.

    Extracted from _execute_prompt so that response formatting stays
    separate from transport logic.

    Args:
        response: A successful AgentResponse from HermesClient.

    Returns:
        0 always (caller checks success before calling this).
    """
    print_success("  Hermes Response:")
    for line in response.content.split("\n"):  # type: ignore[attr-defined]
        print_info(f"    {line}")

    print_info("─" * 60)
    print_info(f"  Session ID:     {response.metadata.get('session_id')}")  # type: ignore[attr-defined]
    print_info(f"  Execution time: {response.execution_time:.2f}s")  # type: ignore[attr-defined]
    print_info(f"  Backend used:   {response.metadata.get('backend', 'N/A')}")  # type: ignore[attr-defined]
    return 0


def _execute_prompt(hermes_client: object, prompt: str, session_id: Optional[str]) -> int:
    """Send a prompt to Hermes and format the response.

    Args:
        hermes_client: An initialized HermesClient instance.
        prompt: The user prompt to send.
        session_id: Optional session ID for stateful multi-turn conversation.

    Returns:
        0 on success, 1 on any failure.
    """
    print_info("─" * 60)
    print_success(f"  User Prompt: {prompt}")
    if session_id:
        print_info(f"  Session ID:  {session_id}")
    print_info("─" * 60)

    try:
        from codomyrmex.agents.hermes import HermesError  # noqa: F401

        response = hermes_client.chat_session(prompt=prompt, session_id=session_id)  # type: ignore[attr-defined]

        if response.is_success():
            return _format_response(response)
        else:
            print_error(f"  Error: {response.error}")
            return 1

    except ImportError as e:
        print_error(f"Cannot import HermesError: {e}")
        return 1
    except Exception as e:
        print_error(f"  Unexpected error during prompt execution: {e}")
        return 1


def main() -> int:
    # Load config for defaults *before* parsing so YAML values seed argparse defaults
    hermes_cfg = _resolve_config()
    config_default_prompt: str = hermes_cfg.get("default_prompt", _DEFAULT_PROMPT)
    log_level: str = hermes_cfg.get("observability", {}).get("log_level", "INFO")

    parser = argparse.ArgumentParser(description="Run the Hermes Agent with a real prompt.")
    parser.add_argument(
        "--prompt",
        type=str,
        default=config_default_prompt,
        help=f"The prompt to send to the Hermes agent (default from hermes.yaml or: '{config_default_prompt}').",
    )
    parser.add_argument(
        "--session",
        type=str,
        default=_DEFAULT_SESSION,
        help="Optional session ID for stateful multi-turn conversation.",
    )
    args = parser.parse_args()

    setup_logging()
    print_info("═" * 60)
    print_info("  Hermes Agent — Real Execution")
    print_info("═" * 60)

    # Decouple HermesClient import via factory helper
    hermes_client = _load_hermes_client()
    if hermes_client is None:
        return 1

    _print_client_info(hermes_client)

    if hermes_client.active_backend == "none":  # type: ignore[attr-defined]
        print_error("No backend available. Install 'hermes' CLI or 'ollama'.")
        return 1

    result = _execute_prompt(hermes_client, args.prompt, args.session)
    if result != 0:
        return result

    print_info("─" * 60)
    print_success("Hermes agent execution complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
```
