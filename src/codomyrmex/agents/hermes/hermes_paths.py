"""Resolve the single NousResearch hermes-agent checkout used across Codomyrmex.

All Hermes surfaces (``HermesClient``, evolution tooling, integration tests that
load upstream ``tools/``) share the same discovery order so one environment
variable pins the tree.

Environment variables
---------------------
HERMES_AGENT_REPO
    Path to a clone of https://github.com/NousResearch/hermes-agent (highest
    priority).
HERMES_CLI_PATH
    Optional absolute path to the ``hermes`` executable. When unset,
    :func:`discover_hermes_cli_binary` checks ``venv/bin/hermes`` and
    ``.venv/bin/hermes`` under the resolved repo, then ``PATH``.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

ENV_HERMES_AGENT_REPO = "HERMES_AGENT_REPO"
ENV_HERMES_CLI_PATH = "HERMES_CLI_PATH"


def _hermes_module_dir() -> Path:
    return Path(__file__).resolve().parent


def default_home_hermes_agent() -> Path:
    """Standard install location used by ``hermes`` installers (data + checkout)."""
    return Path.home() / ".hermes" / "hermes-agent"


def _sibling_hermes_agent_under_src() -> Path | None:
    """``src/hermes-agent`` next to the ``src/codomyrmex`` package (monorepo layout)."""
    mod = _hermes_module_dir()
    codomyrmex_pkg = mod.parent.parent.parent
    src_dir = codomyrmex_pkg.parent
    candidate = src_dir / "hermes-agent"
    return candidate if candidate.is_dir() else None


def discover_hermes_agent_repo() -> Path | None:
    """Return the hermes-agent checkout directory, or ``None`` if not found."""
    env_path = os.environ.get(ENV_HERMES_AGENT_REPO)
    if env_path:
        p = Path(env_path).expanduser().resolve()
        if p.is_dir():
            return p

    home = default_home_hermes_agent()
    if home.is_dir():
        return home.resolve()

    sibling = _sibling_hermes_agent_under_src()
    if sibling is not None:
        return sibling.resolve()

    return None


def require_hermes_agent_repo() -> Path:
    """Like :func:`discover_hermes_agent_repo` but raises if no checkout exists."""
    found = discover_hermes_agent_repo()
    if found is None:
        home = default_home_hermes_agent()
        msg = (
            f"Cannot find hermes-agent checkout. Set {ENV_HERMES_AGENT_REPO} to your "
            f"clone of NousResearch/hermes-agent, or install under {home}"
        )
        raise FileNotFoundError(msg)
    return found


def discover_hermes_cli_binary() -> str | None:
    """Resolve the ``hermes`` executable: env, repo virtualenvs, then ``PATH``."""
    env_cli = os.environ.get(ENV_HERMES_CLI_PATH)
    if env_cli:
        p = Path(env_cli).expanduser().resolve()
        if p.is_file():
            return str(p)

    root = discover_hermes_agent_repo()
    if root is not None:
        for rel in ("venv/bin/hermes", ".venv/bin/hermes"):
            cand = (root / rel).resolve()
            if cand.is_file():
                return str(cand)

    return shutil.which("hermes")
