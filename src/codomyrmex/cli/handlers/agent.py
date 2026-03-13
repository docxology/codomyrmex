"""CLI handler for agent management subcommands.

Provides ``codomyrmex agent start``, ``codomyrmex agent list``,
and ``codomyrmex agent health`` commands.

Example::

    codomyrmex agent list
    codomyrmex agent start hermes --model gemma3
    codomyrmex agent health hermes
"""

from __future__ import annotations

from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_AGENT_DIR = Path(__file__).resolve().parents[2] / "agents"


def handle_agent_list() -> list[str]:
    """List all available agents.

    Scans ``src/codomyrmex/agents/`` for subdirectories with ``__init__.py``.

    Returns:
        List of agent names.
    """
    agents = []
    if _AGENT_DIR.exists():
        for d in sorted(_AGENT_DIR.iterdir()):
            if (
                d.is_dir()
                and (d / "__init__.py").exists()
                and not d.name.startswith("_")
            ):
                agents.append(d.name)

    print(f"📋 Available agents ({len(agents)}):\n")
    for a in agents:
        readme = _AGENT_DIR / a / "README.md"
        desc = ""
        if readme.exists():
            first_line = readme.read_text(errors="replace").strip().splitlines()
            if first_line:
                desc = first_line[0].lstrip("# ").strip()
        print(f"  • {a:20s} {desc}")
    return agents


def handle_agent_start(
    name: str,
    model: str = "gemma3",
    port: int = 0,
) -> dict:
    """Start a named agent.

    Args:
        name: Agent name (e.g., ``hermes``, ``claude``).
        model: LLM model to use.
        port: Optional port for agent server.

    Returns:
        Agent status dict.
    """
    agent_path = _AGENT_DIR / name
    if not agent_path.exists():
        print(f"❌ Agent '{name}' not found. Use 'codomyrmex agent list'.")
        return {"status": "error", "agent": name}

    print(f"🚀 Starting agent '{name}' with model '{model}'...")

    # Check for agent-specific entry point
    config = {
        "agent": name,
        "model": model,
        "status": "started",
    }

    # Try to import agent module
    try:
        import importlib

        mod = importlib.import_module(f"codomyrmex.agents.{name}")
        if hasattr(mod, "start"):
            result = mod.start(model=model, port=port)
            config["result"] = str(result)
            print(f"✅ Agent '{name}' started successfully")
        else:
            print(f"⚠️  Agent '{name}' loaded but has no start() function")
            config["status"] = "loaded"
    except ImportError as e:
        print(f"⚠️  Could not import agent '{name}': {e}")
        config["status"] = "import_error"
    except Exception as e:
        print(f"❌ Error starting agent '{name}': {e}")
        config["status"] = "error"

    return config


def handle_agent_health(name: str) -> dict:
    """Check health of a named agent.

    Args:
        name: Agent name.

    Returns:
        Health status dict.
    """
    agent_path = _AGENT_DIR / name
    status = {
        "agent": name,
        "exists": agent_path.exists(),
        "has_init": (agent_path / "__init__.py").exists()
        if agent_path.exists()
        else False,
        "has_readme": (agent_path / "README.md").exists()
        if agent_path.exists()
        else False,
        "has_tests": bool(list(agent_path.glob("test_*.py")))
        if agent_path.exists()
        else False,
    }

    health = (
        "healthy"
        if all([status["exists"], status["has_init"], status["has_readme"]])
        else "degraded"
    )
    status["health"] = health

    icon = "✅" if health == "healthy" else "⚠️"
    print(f"{icon} Agent '{name}': {health}")
    for key, val in status.items():
        if key not in ("agent", "health"):
            print(f"  {key}: {'✅' if val else '❌'}")

    return status


__all__ = [
    "handle_agent_health",
    "handle_agent_list",
    "handle_agent_start",
]
