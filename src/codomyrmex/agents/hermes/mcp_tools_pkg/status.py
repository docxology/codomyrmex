"""Hermes MCP tools — status category."""

from __future__ import annotations

import sys
from typing import Any

from codomyrmex.agents.hermes.mcp_tools_pkg._client import _get_client
from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="hermes",
    description=(
        "Check Hermes agent availability and configuration. "
        "Reports which backend (CLI / Ollama) is active."
    ),
)
def hermes_status() -> dict[str, Any]:
    """Check Hermes configuration.

    Returns:
        dict with active_backend, cli_available, ollama_available, ollama_model

    """
    try:
        client = _get_client()
        info = client.get_hermes_status()
        return {"status": "success", "available": info.get("success", False), **info}
    except Exception as exc:
        return {"status": "error", "available": False, "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Check live system resource metrics (RAM, CPU, Swap). "
        "Use this proactively to check if the host has enough memory before dispatching heavy tasks."
    ),
)
def hermes_system_health() -> dict[str, Any]:
    """Retrieve realtime hardware usage metrics.

    Returns:
        dict with status and hardware metrics.

    """
    try:
        from codomyrmex.agents.hermes.monitoring import _get_system_metrics

        metrics = _get_system_metrics()
        return {
            "status": "success",
            "metrics": metrics,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Check if a dependency is present in the project's lockfile (`uv.lock`). "
        "Use this to verify if uninstalled packages are causing execution failures."
    ),
)
def hermes_check_dependencies(package_name: str) -> dict[str, Any]:
    """Check for package presence in the environment lockfile.

    Args:
        package_name: The name of the PyPI package to check (e.g. 'requests').

    Returns:
        dict with status, exists boolean, and message.

    """
    try:
        from codomyrmex.environment_setup.lockfile import LockfileParser

        parser = LockfileParser()
        exists = parser.check_dependency(package_name)
        return {
            "status": "success",
            "package": package_name,
            "exists": exists,
            "message": f"Package '{package_name}' is {'present' if exists else 'missing'} in the uv.lock",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Hot-reload the Hermes MCP server configuration. "
        "Re-reads ~/.hermes/mcp_servers.json and signals Hermes to reconnect."
    ),
)
def hermes_mcp_reload() -> dict[str, Any]:
    """Hot-reload MCP server configuration.

    Returns:
        dict with keys: status, servers_loaded, output

    """
    try:
        from codomyrmex.agents.hermes._provider_router import MCPBridgeManager

        bridge = MCPBridgeManager()
        result = bridge.reload()
        return {"status": "success", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Manage cross-session user context for the Hermes agent. "
        "Stores and retrieves user preferences and coding observations."
    ),
)
def hermes_user_context(
    action: str = "get",
    key: str | None = None,
    value: str | None = None,
) -> dict[str, Any]:
    """Manage Hermes cross-session user model.

    Args:
        action: ``"get"`` to retrieve context, ``"set"`` to set a preference,
            ``"observe"`` to record an observation.
        key: Preference key (for ``"set"`` action).
        value: Value to set or observation text.

    Returns:
        dict with keys: status, context or preference data

    """
    try:
        from codomyrmex.agents.hermes._provider_router import UserModel

        model = UserModel()

        if action == "get":
            return {
                "status": "success",
                "context_prompt": model.get_context_prompt(),
                "profile": model.profile,
            }
        if action == "set" and key and value:
            model.set_preference(key, value)
            return {"status": "success", "message": f"set {key}={value}"}
        if action == "observe" and value:
            model.add_observation(value)
            return {
                "status": "success",
                "message": f"Recorded observation: {value[:60]}...",
            }
        return {
            "status": "error",
            "message": f"Invalid action '{action}' or missing key/value",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description="Run hermes doctor for comprehensive health diagnostics (CLI v0.2.0+).",
)
def hermes_doctor() -> dict[str, Any]:
    """Run Hermes health diagnostics.

    Returns:
        dict with keys: status, output, stderr, exit_code

    """
    try:
        client = _get_client()
        result = client.run_doctor()
        return {"status": "success" if result.get("success") else "error", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description="Get the installed Hermes CLI version string.",
)
def hermes_version() -> dict[str, Any]:
    """Get Hermes CLI version.

    Returns:
        dict with keys: status, version

    """
    try:
        client = _get_client()
        version = client.get_version()
        return {
            "status": "success" if version else "unavailable",
            "version": version,
            "cli_available": client._cli_available,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Check the status of the Honcho AI memory integration. "
        "Honcho provides persistent cross-session memory for Hermes."
    ),
)
def hermes_honcho_status() -> dict[str, Any]:
    """Check Honcho memory integration status.

    Returns:
        dict with keys: status, output, exit_code

    """
    try:
        import os
        import shutil
        import subprocess

        hermes_bin = shutil.which("hermes")
        if not hermes_bin:
            return {"status": "error", "message": "Hermes CLI not available"}

        result = subprocess.run(
            [hermes_bin, "honcho", "status"],
            capture_output=True,
            text=True,
            timeout=15,
            env={**os.environ, "NO_COLOR": "1"},
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "honcho status timed out"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Show Hermes usage insights and analytics — token usage, costs, "
        "tool patterns, and activity trends."
    ),
)
def hermes_insights(days: int = 30) -> dict[str, Any]:
    """Get Hermes usage insights.

    Args:
        days: Number of days to analyze (default 30).

    Returns:
        dict with keys: status, output, exit_code

    """
    try:
        import os
        import shutil
        import subprocess

        hermes_bin = shutil.which("hermes")
        if not hermes_bin:
            return {"status": "error", "message": "Hermes CLI not available"}

        result = subprocess.run(
            [hermes_bin, "insights", "--days", str(days)],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "NO_COLOR": "1"},
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "insights timed out"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Get the credential and availability status for all configured "
        "inference providers (OpenRouter, Ollama, Anthropic, etc.)."
    ),
)
def hermes_provider_status() -> dict[str, Any]:
    """Check multi-provider credential status.

    Returns:
        dict with keys: status, providers (dict per provider)

    """
    try:
        from codomyrmex.agents.hermes._provider_router import ProviderRouter

        router = ProviderRouter()
        return {"status": "success", "providers": router.get_provider_status()}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Check the current model rotation state, including health, priorities, "
        "and active cooldown periods for free OpenRouter models."
    ),
)
def hermes_rotation_status() -> dict[str, Any]:
    """Check LLM rotation configuration and health.

    Returns:
        dict with keys: status, rotation_models, active_cooldowns

    """
    try:
        client = _get_client()
        router = client._router
        models = router.get_rotation_models()
        import time

        now = time.time()
        cooldowns = {
            m_id: f"{int(expiry - now)}s remaining"
            for m_id, expiry in router._cooldowns.items()
            if expiry > now
        }
        return {
            "status": "success",
            "rotation_models": models,
            "active_cooldowns": cooldowns,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Perform a comprehensive health check of the Hermes agent subsystem. "
        "Verifies CLI binary, Ollama backend, API keys, and session database integrity."
    ),
)
def hermes_health_check() -> dict[str, Any]:
    """Deep diagnostic check for Hermes.

    Returns:
        dict with diagnostic report

    """
    try:
        client = _get_client()
        status = client.get_hermes_status()

        # Check sessions DB
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        with SQLiteSessionStore(client._session_db_path) as store:
            db_stats = store.get_stats()

        # Check rotation models
        models = client._router.get_rotation_models()

        return {
            "status": "success",
            "backends": status,
            "database": db_stats,
            "rotation_config": {
                "active_models": len(models),
                "path": client._router._rotation_path,
            },
            "environment": {
                "python_version": sys.version.split()[0],
                "platform": sys.platform,
            },
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Query the status of all running Hermes gateway instances. "
        "Returns each instance name, running state, and active model (v0.4.0+)."
    ),
)
def hermes_gateway_status() -> dict[str, Any]:
    """Get live status for all Hermes gateway instances.

    Returns:
        dict with keys: status, instances (list), output
    """
    try:
        client = _get_client()
        result = client.get_gateway_status()
        return {
            "status": "success" if result.get("success") else "error",
            "instances": result.get("instances", []),
            "output": result.get("output", ""),
            "error": result.get("error", ""),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "instances": []}


@mcp_tool(
    category="hermes",
    description=(
        "Look up context length, tool-use support, and provider metadata for a "
        "given model ID. Queries the Hermes model catalog first, then falls "
        "back to the CLI (v0.4.0 model metadata expansion)."
    ),
)
def hermes_model_info(model_id: str) -> dict[str, Any]:
    """Retrieve metadata for a specific model ID.

    Args:
        model_id: OpenRouter model ID, e.g. ``"nvidia/nemotron-3-super-120b-a12b:free"``.

    Returns:
        dict with keys: status, model_id, context_length, supports_tools, provider, source
    """
    try:
        client = _get_client()
        info = client.get_model_info(model_id)
        return {"status": "success" if "error" not in info else "error", **info}
    except Exception as exc:
        return {"status": "error", "model_id": model_id, "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Send an /approve or /deny command to the Hermes gateway to confirm or "
        "cancel a pending dangerous-command approval request (v0.4.0+). "
        "Use /approve session to approve a command pattern for the entire session."
    ),
)
def hermes_approve_command(
    command: str = "/approve",
    session_id: str | None = None,
) -> dict[str, Any]:
    """Approve or deny a pending gateway command approval.

    Args:
        command: ``"/approve"``, ``"/approve session"``, or ``"/deny"``.
        session_id: Target session ID (optional).

    Returns:
        dict with keys: status, output, error
    """
    valid_commands = {"/approve", "/approve session", "/deny"}
    if command not in valid_commands:
        return {
            "status": "error",
            "message": f"Invalid command '{command}'. Use one of: {valid_commands}",
        }
    try:
        client = _get_client()
        result = client.send_gateway_command(command, session_id=session_id)
        return {
            "status": "success" if result.get("success") else "error",
            "output": result.get("output", ""),
            "error": result.get("error", ""),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "list all paired (approved) users and groups for the Hermes gateway. "
        "Reads $HERMES_HOME/pairing/telegram-approved.json."
    ),
)
def hermes_pairing_list() -> dict[str, Any]:
    """list all approved gateway users and groups.

    Returns:
        dict with keys: status, approved (dict), count
    """
    try:
        import json
        import os
        from pathlib import Path

        hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
        approved_path = hermes_home / "pairing" / "telegram-approved.json"
        if not approved_path.exists():
            return {
                "status": "success",
                "approved": {},
                "count": 0,
                "message": f"No pairing file found at {approved_path}",
            }
        approved = json.loads(approved_path.read_text())
        total = sum(len(v) if isinstance(v, list) else 1 for v in approved.values())
        return {
            "status": "success",
            "approved": approved,
            "count": total,
            "path": str(approved_path),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "approved": {}}


@mcp_tool(
    category="hermes",
    description=(
        "Add a user or group ID to the Hermes gateway pairing approved list "
        "($HERMES_HOME/pairing/telegram-approved.json). "
        "Use platform='telegram' and a numeric Telegram user/chat ID."
    ),
)
def hermes_pairing_add(
    user_id: str,
    platform: str = "telegram",
) -> dict[str, Any]:
    """Add a user or group to the gateway pairing list.

    Args:
        user_id: Numeric user or chat ID to approve.
        platform: Platform name (default ``"telegram"``).

    Returns:
        dict with keys: status, message, approved_count
    """
    try:
        import json
        import os
        from pathlib import Path

        hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
        pairing_dir = hermes_home / "pairing"
        pairing_dir.mkdir(parents=True, exist_ok=True)
        approved_path = pairing_dir / "telegram-approved.json"

        approved: dict[str, list[str]] = {}
        if approved_path.exists():
            approved = json.loads(approved_path.read_text())

        if platform not in approved:
            approved[platform] = []

        if user_id in approved[platform]:
            return {
                "status": "success",
                "message": f"{user_id} already in {platform} approved list",
                "approved_count": len(approved[platform]),
            }

        approved[platform].append(user_id)
        approved_path.write_text(json.dumps(approved, indent=2))

        return {
            "status": "success",
            "message": f"Added {user_id} to {platform} approved list",
            "approved_count": len(approved[platform]),
            "path": str(approved_path),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
