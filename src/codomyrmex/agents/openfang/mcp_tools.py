"""openfang MCP tools — auto-discovered via @mcp_tool decorator."""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from . import HAS_OPENFANG
from .config import get_config
from .update import get_upstream_version


def _import_guard() -> dict[str, Any] | None:
    """Return error dict if openfang binary is not installed, else None."""
    if not HAS_OPENFANG:
        return {
            "status": "error",
            "message": (
                "openfang binary not found on PATH. "
                "Install: curl -fsSL https://openfang.sh/install.sh | sh"
            ),
        }
    return None


def _get_runner(timeout: int | None = None):
    from .core import OpenFangRunner

    return OpenFangRunner(timeout=timeout)


@mcp_tool(
    category="openfang",
    description="Check if openfang is installed, return version and submodule status.",
)
def openfang_check() -> dict[str, Any]:
    """Return installation status, version, and submodule info."""
    from .core import get_openfang_version

    cfg = get_config()
    return {
        "status": "success",
        "installed": HAS_OPENFANG,
        "version": get_openfang_version() if HAS_OPENFANG else "",
        "submodule_initialized": cfg.is_submodule_initialized,
        "upstream_sha": get_upstream_version(),
        "vendor_dir": cfg.vendor_dir,
    }


@mcp_tool(
    category="openfang",
    description="Execute an agent query with openfang and return the response.",
)
def openfang_execute(prompt: str, timeout: int = 120) -> dict[str, Any]:
    """Run an agent query via openfang."""
    guard = _import_guard()
    if guard:
        return guard
    if not prompt.strip():
        return {"status": "error", "message": "prompt must not be empty"}
    try:
        runner = _get_runner(timeout=timeout)
        result = runner.execute(prompt)
        return {"status": "success", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="openfang",
    description="List available openfang autonomous Hands (scheduled agent packages).",
)
def openfang_hands_list() -> dict[str, Any]:
    """List all available Hands with name, description, schedule, and enabled status."""
    guard = _import_guard()
    if guard:
        return guard
    try:
        from .hands import HandsManager

        runner = _get_runner()
        result = runner.hands_list()
        hands = HandsManager.parse_list_output(result["stdout"])
        return {
            "status": "success",
            "hands": [
                {
                    "name": h.name,
                    "description": h.description,
                    "schedule": h.schedule,
                    "enabled": h.enabled,
                }
                for h in hands
            ],
            "raw": result["stdout"],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="openfang",
    description=(
        "Send a message via an openfang channel adapter "
        "(telegram, slack, discord, etc.)."
    ),
)
def openfang_send_message(
    channel: str, target: str, message: str, timeout: int = 30
) -> dict[str, Any]:
    """Send a message to a target via the specified channel adapter."""
    guard = _import_guard()
    if guard:
        return guard
    if not channel.strip():
        return {"status": "error", "message": "channel must not be empty"}
    if not target.strip():
        return {"status": "error", "message": "target must not be empty"}
    if not message.strip():
        return {"status": "error", "message": "message must not be empty"}
    try:
        runner = _get_runner(timeout=timeout)
        result = runner.send_message(channel, target, message)
        return {"status": "success", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="openfang",
    description="Control the openfang WebSocket gateway: start, stop, or get status.",
)
def openfang_gateway(action: str = "status") -> dict[str, Any]:
    """Start, stop, or query the openfang WebSocket gateway."""
    if action not in {"start", "stop", "status"}:
        return {
            "status": "error",
            "message": f"action must be one of: start, stop, status. Got: {action!r}",
        }
    guard = _import_guard()
    if guard:
        return guard
    try:
        runner = _get_runner()
        result = runner.gateway_action(action)
        return {"status": "success", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="openfang",
    description="Show openfang configuration sourced from environment variables.",
)
def openfang_config() -> dict[str, Any]:
    """Return the current openfang configuration (all env-var-sourced values)."""
    cfg = get_config()
    return {
        "status": "success",
        "command": cfg.command,
        "timeout": cfg.timeout,
        "gateway_url": cfg.gateway_url,
        "vendor_dir": cfg.vendor_dir,
        "install_dir": cfg.install_dir,
        "submodule_initialized": cfg.is_submodule_initialized,
        "installed": HAS_OPENFANG,
    }


@mcp_tool(
    category="openfang",
    description=(
        "Pull the latest openfang upstream (git submodule update --remote), "
        "optionally rebuild from Rust source and install the new binary."
    ),
)
def openfang_update(
    rebuild: bool = False,
    install: bool = False,
    vendor_dir: str = "",
    install_dir: str = "",
) -> dict[str, Any]:
    """Sync upstream openfang source; optionally rebuild and install."""
    from .update import build_and_install, build_from_source, update_submodule

    sync = update_submodule(vendor_dir=vendor_dir)
    if sync["status"] != "success":
        return sync
    upstream_sha = get_upstream_version(vendor_dir=vendor_dir)
    if not rebuild:
        return {
            "status": "success",
            "upstream_synced": True,
            "upstream_sha": upstream_sha,
            "note": (
                "Pass rebuild=True to compile from source, "
                "install=True to also install the binary."
            ),
        }
    if install:
        build = build_and_install(vendor_dir=vendor_dir, install_dir=install_dir)
    else:
        build = build_from_source(vendor_dir=vendor_dir)
    return {
        "status": build["status"],
        "upstream_synced": True,
        "upstream_sha": upstream_sha,
        **{k: v for k, v in build.items() if k != "status"},
    }
