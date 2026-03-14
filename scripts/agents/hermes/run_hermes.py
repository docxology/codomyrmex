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

# Bootstrap path only — not needed when package is already installed
try:
    from codomyrmex.agents.core.config import get_config
except ImportError:
    sys.path.insert(
        0, str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    )
    from codomyrmex.agents.core.config import get_config

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)

# ── Module-level constants (overridden by hermes.yaml / CLI args) ──────
_DEFAULT_PROMPT = "Explain what Hermes Agent is in one sentence."
_DEFAULT_SESSION: str | None = None


def _resolve_config() -> dict:
    """Load agent config and extract Hermes-specific settings.

    Returns:
        Flat dict of effective hermes config values.
    """
    try:
        config = get_config()
        return config.get("hermes", {}) if isinstance(config, dict) else {}
    except (OSError, ImportError):
        return {}


def _load_hermes_client() -> object | None:
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


def _format_response(response: object, quiet: bool = False) -> int:
    """Render a successful Hermes response to stdout via cli_helpers.

    Extracted from _execute_prompt so that response formatting stays
    separate from transport logic.

    Args:
        response: A successful AgentResponse from HermesClient.
        quiet: If True, print only the response content (no metadata).

    Returns:
        0 always (caller checks success before calling this).
    """
    if quiet:
        print(response.content)
        return 0

    print_success("  Hermes Response:")
    for line in response.content.split("\n"):  # type: ignore[attr-defined]
        print_info(f"    {line}")

    print_info("─" * 60)
    print_info(f"  Session ID:     {response.metadata.get('session_id')}")  # type: ignore[attr-defined]
    print_info(f"  Execution time: {response.execution_time:.2f}s")  # type: ignore[attr-defined]
    print_info(f"  Backend used:   {response.metadata.get('backend', 'N/A')}")  # type: ignore[attr-defined]
    session_name = response.metadata.get("session_name")  # type: ignore[attr-defined]
    if session_name:
        print_info(f"  Session name:   {session_name}")
    return 0


def _execute_prompt(
    hermes_client: object,
    prompt: str,
    session_id: str | None,
    session_name: str | None = None,
    quiet: bool = False,
) -> int:
    """Send a prompt to Hermes and format the response.

    Args:
        hermes_client: An initialized HermesClient instance.
        prompt: The user prompt to send.
        session_id: Optional session ID for stateful multi-turn conversation.
        session_name: Optional human-friendly session name (v0.2.0 feature).
        quiet: If True, suppress verbose output.

    Returns:
        0 on success, 1 on any failure.
    """
    if not quiet:
        print_info("─" * 60)
        print_success(f"  User Prompt: {prompt}")
        if session_id:
            print_info(f"  Session ID:  {session_id}")
        if session_name:
            print_info(f"  Session Name: {session_name}")
        print_info("─" * 60)

    try:
        from codomyrmex.agents.hermes import HermesError

        response = hermes_client.chat_session(
            prompt=prompt,
            session_id=session_id,
            session_name=session_name,
        )  # type: ignore[attr-defined]

        if response.is_success():
            return _format_response(response, quiet=quiet)
        print_error(f"  Error: {response.error}")
        return 1

    except ImportError as e:
        print_error(f"Cannot import HermesError: {e}")
        return 1
    except TypeError:
        # Fallback if chat_session doesn't accept session_name yet
        response = hermes_client.chat_session(prompt=prompt, session_id=session_id)  # type: ignore[attr-defined]
        if response.is_success():
            return _format_response(response, quiet=quiet)
        print_error(f"  Error: {response.error}")
        return 1
    except Exception as e:
        print_error(f"  Unexpected error during prompt execution: {e}")
        return 1


def main() -> int:
    # Load config for defaults *before* parsing so YAML values seed argparse defaults
    hermes_cfg = _resolve_config()
    config_default_prompt: str = hermes_cfg.get("default_prompt", _DEFAULT_PROMPT)

    parser = argparse.ArgumentParser(
        description="Run the Hermes Agent with a real prompt."
    )
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
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Human-friendly session name (v0.2.0). Creates or resumes a named session.",
    )
    parser.add_argument(
        "--quiet",
        "-Q",
        action="store_true",
        default=False,
        help="Quiet mode: suppress banners/metadata, print only the raw response. For CI/CD and programmatic use.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override the default model (e.g. 'hermes3', 'qwen2.5-coder'). Routes through 'hermes model' for CLI.",
    )
    parser.add_argument(
        "--worktree",
        action="store_true",
        default=False,
        help="Run in an isolated git worktree (v0.2.0). Changes are isolated and mergeable via 'git merge'.",
    )
    args = parser.parse_args()

    setup_logging()

    if not args.quiet:
        print_info("═" * 60)
        print_info("  Hermes Agent — Real Execution")
        print_info("═" * 60)

    # Decouple HermesClient import via factory helper
    hermes_client = _load_hermes_client()
    if hermes_client is None:
        return 1

    if not args.quiet:
        _print_client_info(hermes_client)

    if hermes_client.active_backend == "none":  # type: ignore[attr-defined]
        print_error("No backend available. Install 'hermes' CLI or 'ollama'.")
        return 1

    # Worktree isolation (v0.2.0): create isolated git worktree for this session
    worktree_path = None
    session_id_for_worktree = args.session or args.name
    if args.worktree and session_id_for_worktree:
        worktree_path = hermes_client.create_worktree(session_id_for_worktree)  # type: ignore[attr-defined]
        if worktree_path:
            if not args.quiet:
                print_info(f"  Worktree: {worktree_path}")
        elif not args.quiet:
            print_info("  Worktree creation failed; running in main tree.")

    result = _execute_prompt(
        hermes_client,
        args.prompt,
        args.session,
        session_name=args.name,
        quiet=args.quiet,
    )

    # Cleanup worktree if auto_cleanup is enabled
    if worktree_path and session_id_for_worktree:
        hermes_client.cleanup_worktree(session_id_for_worktree)  # type: ignore[attr-defined]

    if result != 0:
        return result

    if not args.quiet:
        print_info("─" * 60)
        print_success("Hermes agent execution complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
