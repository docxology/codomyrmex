"""MCP server hot-reload bridge."""

from __future__ import annotations

import json
import logging
import os
import shutil
import signal
import subprocess
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)

class MCPBridgeManager:
    """Manage the Hermes ↔ Codomyrmex MCP bridge.

    Handles configuration of Hermes v0.2.0 native MCP client to load
    Codomyrmex MCP servers, and supports hot-reloading without session
    restart.

    Attributes:
        config_path: Path to the MCP servers config file.
        servers: Currently configured server definitions.

    """

    def __init__(self, config_path: str | None = None) -> None:
        """Initialize MCP bridge manager.

        Args:
            config_path: Path to MCP servers JSON config.

        """
        self._config_path = Path(
            config_path or os.path.expanduser("~/.hermes/mcp_servers.json")
        )
        self._servers: dict[str, dict[str, Any]] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load MCP server configuration from disk."""
        if self._config_path.exists():
            try:
                self._servers = json.loads(self._config_path.read_text())
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to load MCP config: %s", exc)

    def save_config(self) -> None:
        """Persist current MCP server configuration."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config_path.write_text(json.dumps(self._servers, indent=2))
        logger.info("Saved MCP config to %s", self._config_path)

    def register_server(
        self,
        name: str,
        *,
        command: str,
        args: list[str] | None = None,
        transport: str = "stdio",
        description: str = "",
    ) -> None:
        """Register an MCP server for Hermes to consume.

        Args:
            name: Server identifier.
            command: Command to launch the server.
            args: Optional command arguments.
            transport: Transport mechanism (``"stdio"`` or ``"http"``).
            description: Human-readable description.

        """
        self._servers[name] = {
            "command": command,
            "args": args or [],
            "transport": transport,
            "description": description,
        }
        self.save_config()
        logger.info("Registered MCP server '%s' (%s via %s)", name, command, transport)

    def unregister_server(self, name: str) -> bool:
        """Remove an MCP server registration.

        Args:
            name: Server identifier to remove.

        Returns:
            True if the server was found and removed.

        """
        if name in self._servers:
            del self._servers[name]
            self.save_config()
            return True
        return False

    def reload(self) -> dict[str, Any]:
        """Hot-reload MCP server configuration.

        Re-reads the config from disk and signals any running Hermes
        process to reload its MCP connections.

        Returns:
            dict with ``success`` and ``servers_loaded`` count.

        """
        self._load_config()
        server_count = len(self._servers)
        logger.info("Hot-reloaded MCP config: %d servers", server_count)

        # Signal Hermes CLI to reload if possible (v0.2.0 `hermes mcp reload`)
        hermes_bin = shutil.which("hermes")
        if hermes_bin:
            try:
                result = subprocess.run(
                    [hermes_bin, "mcp", "reload"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                return {
                    "success": result.returncode == 0,
                    "servers_loaded": server_count,
                    "output": result.stdout.strip(),
                }
            except Exception as exc:
                logger.debug(
                    "MCP reload via CLI failed (may not be supported): %s", exc
                )

        return {
            "success": True,
            "servers_loaded": server_count,
            "output": "Config reloaded (CLI signal skipped)",
        }

    @property
    def servers(self) -> dict[str, dict[str, Any]]:
        """Return current server configurations (deep copy)."""
        import copy

        return copy.deepcopy(self._servers)

    def list_servers(self) -> list[dict[str, Any]]:
        """list all configured MCP servers.

        Returns:
            list of server info dicts with ``name``, ``command``, ``transport``.

        """
        return [{"name": name, **config} for name, config in self._servers.items()]
