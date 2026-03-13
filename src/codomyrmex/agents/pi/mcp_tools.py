"""MCP tools for the Pi coding agent.

Exposes Pi capabilities via Model Context Protocol so that sibling agents,
swarm orchestrators, and external MCP clients can invoke Pi programmatically.
"""

from __future__ import annotations

import shutil
from typing import Any, Dict

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**_kw):  # type: ignore[misc]
        """Fallback no-op decorator when MCP framework not available."""
        def _wrap(fn):  # type: ignore[misc]
            return fn
        return _wrap

from .pi_client import PiClient, PiConfig, PiError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client(**overrides: Any) -> PiClient:
    """Build a PiClient from keyword overrides."""
    cfg_keys = set(PiConfig.__dataclass_fields__)
    cfg = {k: v for k, v in overrides.items() if k in cfg_keys and v}
    return PiClient(config=cfg)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp_tool(
    name="pi_status",
    description="Check whether the pi coding agent CLI is installed and report its version.",
    category="pi",
)
def pi_status() -> dict[str, Any]:
    """Return installation status and version of pi."""
    pi_bin = shutil.which("pi")
    if not pi_bin:
        return {"status": "not_installed", "message": "pi CLI not found on PATH"}

    import subprocess
    try:
        result = subprocess.run(
            [pi_bin, "--version"],
            capture_output=True, text=True, timeout=10,
        )
        version = result.stdout.strip()
        return {"status": "installed", "version": version, "path": pi_bin}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    name="pi_prompt",
    description="Send a prompt to the pi coding agent in non-interactive (print) mode and return the response.",
    category="pi",
)
def pi_prompt(
    message: str,
    provider: str = "google",
    model: str = "",
    thinking: str = "",
    tools: str = "read,bash,edit,write",
    cwd: str = "",
    timeout: float = 120.0,
) -> dict[str, Any]:
    """Run ``pi -p <message>`` and return the result."""
    try:
        cfg: dict[str, Any] = {"provider": provider, "tools": tools}
        if model:
            cfg["model"] = model
        if thinking:
            cfg["thinking"] = thinking
        if cwd:
            cfg["cwd"] = cwd
        client = PiClient(config=cfg)
        output = client.run_print(message, timeout=timeout)
        return {"status": "success", "output": output}
    except PiError as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    name="pi_list_models",
    description="List available models for a provider via pi --list-models.",
    category="pi",
)
def pi_list_models(
    search: str = "",
    provider: str = "",
) -> dict[str, Any]:
    """Run ``pi --list-models [search]`` and return output."""
    import subprocess
    pi_bin = shutil.which("pi") or "pi"
    cmd = [pi_bin, "--list-models"]
    if search:
        cmd.append(search)
    if provider:
        cmd += ["--provider", provider]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15,
        )
        lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        return {"status": "success", "models": lines, "count": len(lines)}
    except FileNotFoundError:
        return {"status": "error", "message": "pi CLI not found"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    name="pi_start_rpc",
    description="Start a pi RPC session for multi-turn interaction.",
    category="pi",
)
def pi_start_rpc(
    provider: str = "google",
    model: str = "",
    no_session: bool = True,
) -> dict[str, Any]:
    """Start a pi RPC subprocess and return a session handle.

    Note: In practice the caller should use PiClient directly for
    multi-turn interaction.  This tool is primarily informational.
    """
    try:
        cfg: dict[str, Any] = {
            "provider": provider,
            "no_session": no_session,
        }
        if model:
            cfg["model"] = model
        client = PiClient(config=cfg)
        client.start()
        pid = client._proc.pid if client._proc else None
        return {
            "status": "success",
            "pid": pid,
            "message": f"Pi RPC session started (PID {pid})",
        }
    except PiError as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    name="pi_install_package",
    description="Install a pi package from npm or git.",
    category="pi",
)
def pi_install_package(source: str) -> dict[str, Any]:
    """Run ``pi install <source>``."""
    import subprocess
    pi_bin = shutil.which("pi") or "pi"
    try:
        result = subprocess.run(
            [pi_bin, "install", source],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout.strip()}
        return {"status": "error", "message": result.stderr.strip() or result.stdout.strip()}
    except FileNotFoundError:
        return {"status": "error", "message": "pi CLI not found"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    name="pi_list_packages",
    description="List installed pi packages.",
    category="pi",
)
def pi_list_packages() -> dict[str, Any]:
    """Run ``pi list``."""
    import subprocess
    pi_bin = shutil.which("pi") or "pi"
    try:
        result = subprocess.run(
            [pi_bin, "list"],
            capture_output=True, text=True, timeout=15,
        )
        return {"status": "success", "output": result.stdout.strip()}
    except FileNotFoundError:
        return {"status": "error", "message": "pi CLI not found"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
