#!/usr/bin/env python3
"""Hermes Agent — Thin Orchestrator Setup Script.

Validates the environment, configuration, and backend binaries required
for the Codomyrmex Hermes Agent to run properly.

Usage:
    python scripts/agents/hermes/setup_hermes.py
    uv run python scripts/agents/hermes/setup_hermes.py
"""

import shutil
import sys
from pathlib import Path

# Bootstrap path only — avoids polluting sys.path when already installed
try:
    from codomyrmex.agents.core.config import get_config
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))
    from codomyrmex.agents.core.config import get_config

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)

# Repo-relative path constants (resolved once at module load, not hardcoded strings)
_REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
_HERMES_CONFIG_PATH: Path = _REPO_ROOT / "config" / "agents" / "hermes.yaml"


def _check_imports() -> bool:
    """Verify that HermesClient and related modules can be imported.

    Returns:
        True if all imports succeed, False otherwise.
    """
    try:
        from codomyrmex.agents.hermes import HermesClient  # noqa: F401
        print_success("  ✓ Core modules imported successfully.")
        return True
    except Exception as e:
        print_error(f"  ✗ Core module import failed: {e}")
        return False


def _check_config() -> bool:
    """Verify agent configuration loads successfully and hermes.yaml exists.

    Returns:
        True if configuration is healthy, False otherwise.
    """
    try:
        get_config()
        print_success("  ✓ Configuration loaded successfully.")
    except Exception as exc:
        print_error(f"  ✗ Configuration load failed: {exc}")
        return False

    if _HERMES_CONFIG_PATH.exists():
        print_success(f"  ✓ Found hermes-specific config at {_HERMES_CONFIG_PATH.name}")
        return True
    else:
        print_error(f"  ! Missing hermes-specific config at {_HERMES_CONFIG_PATH.name}")
        return False


def _check_backends() -> tuple[bool, bool]:
    """Detect which execution backends are available on PATH.

    Returns:
        Tuple of (cli_installed, ollama_installed).
    """
    print_info("\n  Checking Backends...")
    cli_installed: bool = bool(shutil.which("hermes"))
    ollama_installed: bool = bool(shutil.which("ollama"))

    if cli_installed:
        print_success("  ✓ Hermes CLI binary found in PATH.")
    else:
        print_error("  ! Hermes CLI binary NOT found in PATH. (Fallback required)")

    if ollama_installed:
        print_success("  ✓ Ollama CLI found in PATH.")
    else:
        print_error("  ! Ollama CLI NOT found. (Cannot use fallback)")

    return cli_installed, ollama_installed


def _check_session_storage(hermes_client: object) -> bool:
    """Verify that the session SQLite database location is writable.

    Args:
        hermes_client: An initialized HermesClient instance.

    Returns:
        True if storage is ready, False if unrecoverable.
    """
    print_info("\n  Checking Session Storage...")
    db_path: Path = Path(hermes_client._session_db_path)  # type: ignore[attr-defined]
    if db_path.exists():
        print_success(f"  ✓ Session database exists at: {db_path}")
        return True

    print_info(f"  ! Session database does not yet exist at: {db_path}")
    print_info("    (It will be created dynamically on first use)")
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        print_success(f"  ✓ Verified parent directory is writable: {db_path.parent}")
        return True
    except Exception as e:
        print_error(f"  ✗ Cannot write to session storage directory: {e}")
        return False


def main() -> int:
    setup_logging()
    print_info("═" * 60)
    print_info("  Hermes Agent — Setup & Validation")
    print_info("═" * 60)

    # 1. Verify imports
    if not _check_imports():
        return 1

    # 2. Verify config
    _check_config()

    # 3. Check backends
    cli_installed, ollama_installed = _check_backends()
    if not cli_installed and not ollama_installed:
        print_error("\n  CRITICAL: Neither hermes CLI nor ollama CLI is installed.")
        print_error("  The agent will not be able to execute prompts.")
        return 1

    # 4. Verify session storage (instantiate client once backends are confirmed)
    try:
        from codomyrmex.agents.hermes import HermesClient
        hermes_client = HermesClient()
    except Exception as exc:
        print_error(f"  ✗ Failed to initialize HermesClient: {exc}")
        return 1

    if not _check_session_storage(hermes_client):
        return 1

    print_info("─" * 60)
    if hermes_client.active_backend != "none":
        print_success(f"Setup complete. Hermes Agent is READY. (Backend: {hermes_client.active_backend})")
        return 0
    else:
        print_error("Setup incomplete. Hermes Agent is Offline.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
