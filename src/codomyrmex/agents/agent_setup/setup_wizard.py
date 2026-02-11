"""Interactive terminal setup wizard for Codomyrmex agents.

Usage::

    python -m codomyrmex.agents.agent_setup

Walks the user through:
1. Status overview of all registered agents
2. Guided API key / binary path entry for missing agents
3. Live probe after each entry to confirm operative status
4. Optional save to ``~/.codomyrmex/agents.yaml``
"""

from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path

from codomyrmex.agents.agent_setup.registry import AgentRegistry, ProbeResult
from codomyrmex.agents.agent_setup.config_file import (
    DEFAULT_CONFIG_PATH,
    load_config,
    save_config,
)


# ── ANSI helpers ──────────────────────────────────────────────────────────

_BOLD = "\033[1m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RED = "\033[91m"
_CYAN = "\033[96m"
_RESET = "\033[0m"
_DIM = "\033[2m"


def _status_color(status: str) -> str:
    return {
        "operative": _GREEN,
        "key_missing": _YELLOW,
        "unreachable": _RED,
        "unavailable": _DIM,
    }.get(status, _RESET)


def _badge(status: str) -> str:
    color = _status_color(status)
    symbols = {
        "operative": "✓",
        "key_missing": "○",
        "unreachable": "✗",
        "unavailable": "—",
    }
    return f"{color}{symbols.get(status, '?')} {status}{_RESET}"


# ── Display helpers ───────────────────────────────────────────────────────

def print_banner():
    print(f"""
{_BOLD}{_CYAN}╔══════════════════════════════════════════════════════════════╗
║              Codomyrmex Agent Setup Wizard                   ║
╚══════════════════════════════════════════════════════════════╝{_RESET}
""")


def print_status_table(results: list[ProbeResult]):
    """Print a formatted status table."""
    print(f"\n{_BOLD}  {'Agent':<22} {'Type':<8} {'Status':<22} {'Detail'}{_RESET}")
    print("  " + "─" * 72)

    registry = AgentRegistry()
    descs = {d.name: d for d in registry.list_agents()}

    for r in results:
        desc = descs.get(r.name)
        agent_type = desc.agent_type if desc else "?"
        latency = f" ({r.latency_ms:.0f}ms)" if r.latency_ms is not None else ""
        print(f"  {r.name:<22} {agent_type:<8} {_badge(r.status):<32} {r.detail}{latency}")

    operative = sum(1 for r in results if r.is_operative)
    total = len(results)
    print(f"\n  {_BOLD}{operative}/{total} agents operative{_RESET}\n")


# ── Interactive setup ─────────────────────────────────────────────────────

def _prompt_api_key(agent_name: str, env_var: str) -> str | None:
    """Prompt for an API key (hidden input)."""
    print(f"\n  {_CYAN}{agent_name}{_RESET} requires {_BOLD}{env_var}{_RESET}")
    key = getpass.getpass(f"  Enter API key (or press Enter to skip): ")
    return key.strip() or None


def _prompt_binary_path(agent_name: str, binary: str) -> str | None:
    """Prompt for a CLI binary path."""
    print(f"\n  {_CYAN}{agent_name}{_RESET} binary '{binary}' not found")
    path = input(f"  Enter absolute path (or press Enter to skip): ").strip()
    return path or None


def run_setup_wizard(
    config_path: Path | str | None = None,
    non_interactive: bool = False,
):
    """Run the interactive agent setup wizard.

    Args:
        config_path: Override config file path.
        non_interactive: If True, only print status and skip prompts.
    """
    print_banner()

    registry = AgentRegistry()
    existing_config = load_config(config_path)
    agents_config = existing_config.get("agents", {})

    # ── Phase 1: Initial probe ────────────────────────────────────────
    print(f"{_BOLD}Phase 1: Scanning agent availability…{_RESET}")
    results = registry.probe_all()
    print_status_table(results)

    if non_interactive:
        return results

    # ── Phase 2: Guided setup for non-operative agents ────────────────
    missing = [r for r in results if not r.is_operative]
    if not missing:
        print(f"  {_GREEN}All agents are operative — nothing to configure.{_RESET}\n")
        return results

    print(f"{_BOLD}Phase 2: Configure missing agents{_RESET}")
    print(f"  {_DIM}(press Enter to skip any agent){_RESET}\n")

    descs = {d.name: d for d in registry.list_agents()}
    updated = False

    for probe in missing:
        desc = descs.get(probe.name)
        if not desc:
            continue

        value = None
        if desc.agent_type == "api":
            value = _prompt_api_key(desc.display_name, desc.env_var)
            if value:
                # Set in environment for immediate re-probe
                os.environ[desc.env_var] = value
                # Store in config dict
                if desc.name not in agents_config:
                    agents_config[desc.name] = {}
                agents_config[desc.name]["api_key"] = value
                updated = True

        elif desc.agent_type == "cli":
            value = _prompt_binary_path(desc.display_name, desc.env_var)
            if value:
                # Can't easily inject into PATH, but record for config
                if desc.name not in agents_config:
                    agents_config[desc.name] = {}
                agents_config[desc.name]["command"] = value
                updated = True

        elif desc.agent_type == "local":
            print(f"\n  {_CYAN}{desc.display_name}{_RESET}: {probe.detail}")
            url = input(f"  Enter Ollama URL (default http://localhost:11434, Enter to skip): ").strip()
            if url:
                os.environ["OLLAMA_BASE_URL"] = url
                if "ollama" not in agents_config:
                    agents_config["ollama"] = {}
                agents_config["ollama"]["base_url"] = url
                updated = True

        # Live re-probe after entry
        if value or (desc.agent_type == "local" and updated):
            re = registry.probe_agent(desc.name)
            print(f"  → {_badge(re.status)}  {re.detail}")

    # ── Phase 3: Re-probe and save ────────────────────────────────────
    print(f"\n{_BOLD}Phase 3: Final status{_RESET}")
    results = registry.probe_all()
    print_status_table(results)

    if updated:
        existing_config["agents"] = agents_config
        save_choice = input(f"  Save config to {DEFAULT_CONFIG_PATH}? [Y/n] ").strip().lower()
        if save_choice in ("", "y", "yes"):
            path = save_config(existing_config, config_path)
            print(f"  {_GREEN}Saved to {path}{_RESET}")
        else:
            print(f"  {_DIM}Skipped saving.{_RESET}")

    print(f"\n{_BOLD}Setup complete.{_RESET}\n")
    return results
