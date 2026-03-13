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
    from codomyrmex.agents.hermes import HermesClient

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)

# Repo-relative path constants (resolved once at module load, not hardcoded strings)
_REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
_HERMES_CONFIG_PATH: Path = _REPO_ROOT / "config" / "agents" / "hermes.yaml"


def _resolve_hermes_config() -> dict:
    """Load hermes-specific config from the agent config system.

    Returns:
        Hermes config dict, or empty dict on error.
    """
    try:
        config = get_config()
        return config.get("hermes", {}) if isinstance(config, dict) else {}
    except (OSError, ImportError):
        return {}


def _check_imports() -> bool:
    """Verify that HermesClient and related modules can be imported.

    Returns:
        True if all imports succeed, False otherwise.
    """
    try:
        from codomyrmex.agents.hermes import HermesClient
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


def _get_hermes_session_db_path() -> Path:
    """Get the Hermes session database path from configuration.

    Returns:
        Absolute Path to the session database file.
    """
    try:
        config = get_config()
        hermes_config = config.get("hermes", {}) if isinstance(config, dict) else {}
        db_path_str = hermes_config.get("hermes_session_db")
        if db_path_str:
            return Path(db_path_str).expanduser().resolve()
    except Exception:
        pass  # Fall back to default

    # Default path: ~/.codomyrmex/hermes_sessions.db
    return Path.home() / ".codomyrmex" / "hermes_sessions.db"


def _check_hermes_version(hermes_client: object) -> str | None:
    """Detect the installed Hermes CLI version.

    Args:
        hermes_client: An initialized HermesClient instance.

    Returns:
        Version string if detected, None otherwise.
    """
    print_info("\n  Checking Hermes CLI Version...")
    version = hermes_client.get_version()  # type: ignore[attr-defined]
    if version:
        print_success(f"  ✓ Hermes CLI version: {version}")
        # Check for v0.2.0+ features
        try:
            parts = [int(x) for x in version.split(".")[:3]]
            if parts >= [0, 2, 0]:
                print_success("  ✓ v0.2.0+ detected — provider router, MCP client, skills ecosystem available")
            else:
                print_info(f"  ℹ️  Version {version} detected. Consider upgrading: hermes update")
        except (ValueError, IndexError):
            print_info(f"  ℹ️  Version string '{version}' could not be parsed.")
    else:
        print_info("  ℹ️  Version not available (CLI not installed or version command not supported).")
    return version


def _check_hermes_doctor(hermes_client: object) -> bool:
    """Run ``hermes doctor`` for comprehensive health diagnostics.

    Args:
        hermes_client: An initialized HermesClient instance.

    Returns:
        True if doctor reports healthy, False otherwise.
    """
    print_info("\n  Running Hermes Doctor...")
    result: dict = hermes_client.run_doctor()  # type: ignore[attr-defined]
    if result.get("success"):
        output = result.get("output", "")
        # Print first 10 lines of doctor output
        for line in output.splitlines()[:10]:
            print_info(f"    {line}")
        if len(output.splitlines()) > 10:
            print_info(f"    ... ({len(output.splitlines()) - 10} more lines)")
        print_success("  ✓ Hermes doctor: healthy")
        return True
    error = result.get("error", "Unknown error")
    if "not available" in error.lower():
        print_info("  ℹ️  hermes doctor: CLI not available (skipping).")
        return True  # Not a failure — just not available
    print_error(f"  ⚠  hermes doctor reported issues: {error}")
    return False


def _check_session_storage() -> bool:
    """Verify that the session SQLite database location is writable.

    Returns:
        True if storage is ready, False if unrecoverable.
    """
    print_info("\n  Checking Session Storage...")
    db_path: Path = _get_hermes_session_db_path()
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


def _check_mcp_bridge() -> bool:
    """Check MCP bridge configuration for Hermes ↔ Codomyrmex integration.

    Reads the ``mcp_bridge`` section from hermes.yaml and verifies the
    MCP server command is accessible.

    Returns:
        True if MCP bridge is configured (or disabled), False on error.
    """
    print_info("\n  Checking MCP Bridge...")
    hermes_cfg = _resolve_hermes_config()
    mcp_cfg = hermes_cfg.get("mcp_bridge", {})

    if not mcp_cfg.get("enabled", False):
        print_info("  ℹ️  MCP bridge is disabled in hermes.yaml.")
        return True

    servers = mcp_cfg.get("servers", {})
    if not servers:
        print_info("  ℹ️  No MCP servers configured in hermes.yaml.")
        return True

    for name, server_cfg in servers.items():
        cmd = server_cfg.get("command", "")
        transport = server_cfg.get("transport", "stdio")
        desc = server_cfg.get("description", "")
        if shutil.which(cmd):
            print_success(f"  ✓ MCP server '{name}': {cmd} ({transport}) — {desc}")
        else:
            print_info(f"  ⚠  MCP server '{name}': command '{cmd}' not found in PATH")

    return True


def _check_skills(hermes_client: object) -> bool:
    """Check installed Hermes skills.

    Args:
        hermes_client: An initialized HermesClient instance.

    Returns:
        True if skills are accessible or CLI is not available.
    """
    print_info("\n  Checking Skills Inventory...")
    result: dict = hermes_client.list_skills()  # type: ignore[attr-defined]
    if result.get("success"):
        output = result.get("output", "")
        skill_count = len([line for line in output.splitlines() if line.strip() and not line.startswith(" ")])
        print_success(f"  ✓ {skill_count} skills available")
        return True
    error = result.get("error", "")
    if "requires" in error.lower():
        print_info("  ℹ️  Skills listing requires Hermes CLI (not available).")
        return True
    print_info(f"  ℹ️  Skills check: {error}")
    return True


def main() -> int:
    setup_logging()
    print_info("═" * 60)
    print_info("  Hermes Agent — Setup & Validation")
    print_info("═" * 60)

    # 1. Verify imports
    if not _check_imports():
        return 1

    # 2. Verify config
    if not _check_config():
        return 1

    # 3. Check backends
    cli_installed, ollama_installed = _check_backends()
    if not cli_installed and not ollama_installed:
        print_error("\n  CRITICAL: Neither hermes CLI nor ollama CLI is installed.")
        print_error("  The agent will not be able to execute prompts.")
        return 1

    # 4. Verify session storage
    if not _check_session_storage():
        return 1

    # 5. Initialize Hermes client for version/doctor checks
    try:
        from codomyrmex.agents.hermes import HermesClient
        hermes_client = HermesClient()
    except Exception as exc:
        print_error(f"  ✗ Failed to initialize HermesClient: {exc}")
        return 1

    # 6. Check Hermes CLI version (v0.2.0+ unlocks provider router, MCP, skills)
    _check_hermes_version(hermes_client)

    # 7. Run hermes doctor for comprehensive health check
    _check_hermes_doctor(hermes_client)

    # 8. Check MCP bridge configuration
    _check_mcp_bridge()

    # 9. Check skills inventory
    _check_skills(hermes_client)

    print_info("─" * 60)
    if hermes_client.active_backend != "none":
        print_success(f"Setup complete. Hermes Agent is READY. (Backend: {hermes_client.active_backend})")
        return 0
    print_error("Setup incomplete. Hermes Agent is Offline.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
