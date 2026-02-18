"""MCP Client — consume external MCP servers.

Provides a lightweight, protocol-compliant client for connecting to
MCP servers (stdio or HTTP), discovering tools/resources/prompts,
and invoking tools programmatically.

Example::

    async with MCPClient.connect_http("http://localhost:8080") as client:
        tools = await client.list_tools()
        result = await client.call_tool("read_file", {"path": "README.md"})
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class MCPClientConfig:
    """Configuration for an MCP client connection."""

    name: str = "codomyrmex-mcp-client"
    version: str = "0.1.0"
    timeout_seconds: float = 30.0
    protocol_version: str = "2025-06-18"


class MCPClient:
    """Client for consuming external MCP servers.

    Supports stdio and HTTP transports.  Use the class-method factories
    ``connect_stdio`` / ``connect_http`` as async context managers.
    """

    def __init__(self, config: MCPClientConfig | None = None) -> None:
        self.config = config or MCPClientConfig()
        self._request_id = 0
        self._initialized = False
        self._server_info: dict[str, Any] = {}
        self._transport: _Transport | None = None

    # ------------------------------------------------------------------
    # Connection factories
    # ------------------------------------------------------------------

    @classmethod
    def connect_stdio(
        cls,
        command: list[str],
        *,
        config: MCPClientConfig | None = None,
    ) -> _StdioContextManager:
        """Connect to an MCP server over stdio.

        Args:
            command: Command + args to launch the server process.
            config: Optional client configuration.

        Returns:
            Async context manager yielding an ``MCPClient``.
        """
        return _StdioContextManager(command, config)

    @classmethod
    def connect_http(
        cls,
        base_url: str,
        *,
        config: MCPClientConfig | None = None,
    ) -> _HTTPContextManager:
        """Connect to an MCP server over HTTP.

        Args:
            base_url: Server URL (e.g. ``http://localhost:8080``).
            config: Optional client configuration.

        Returns:
            Async context manager yielding an ``MCPClient``.
        """
        return _HTTPContextManager(base_url, config)

    # ------------------------------------------------------------------
    # JSON-RPC helpers
    # ------------------------------------------------------------------

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def _send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a JSON-RPC request and return the response."""
        msg: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {},
        }
        assert self._transport is not None, "Not connected — use a context manager"
        response = await self._transport.send(msg, timeout=self.config.timeout_seconds)
        if "error" in response:
            raise MCPClientError(
                f"RPC error on {method}: {response['error'].get('message', response['error'])}"
            )
        return response.get("result", {})

    async def _notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        """Send a JSON-RPC notification (no response expected)."""
        msg: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }
        assert self._transport is not None
        await self._transport.send_notification(msg)

    # ------------------------------------------------------------------
    # Protocol lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> dict[str, Any]:
        """Perform the MCP initialize handshake."""
        result = await self._send("initialize", {
            "protocolVersion": self.config.protocol_version,
            "clientInfo": {"name": self.config.name, "version": self.config.version},
            "capabilities": {},
        })
        self._server_info = result
        self._initialized = True
        await self._notify("notifications/initialized")
        logger.info(
            "MCP client initialized — server=%s version=%s",
            result.get("serverInfo", {}).get("name", "?"),
            result.get("serverInfo", {}).get("version", "?"),
        )
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def server_info(self) -> dict[str, Any]:
        """Server info returned during initialization."""
        return self._server_info

    async def list_tools(self) -> list[dict[str, Any]]:
        """List tools exposed by the server."""
        result = await self._send("tools/list")
        return result.get("tools", [])

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Invoke a tool on the server.

        Args:
            name: Tool name.
            arguments: Tool arguments dict.

        Returns:
            The tool result dict (``content``, ``structuredContent``, etc.).
        """
        result = await self._send("tools/call", {
            "name": name,
            "arguments": arguments or {},
        })
        return result

    async def list_resources(self) -> list[dict[str, Any]]:
        """List resources exposed by the server."""
        result = await self._send("resources/list")
        return result.get("resources", [])

    async def read_resource(self, uri: str) -> dict[str, Any]:
        """Read a resource by URI."""
        result = await self._send("resources/read", {"uri": uri})
        return result

    async def list_prompts(self) -> list[dict[str, Any]]:
        """List prompt templates exposed by the server."""
        result = await self._send("prompts/list")
        return result.get("prompts", [])

    async def get_prompt(
        self, name: str, arguments: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Get a rendered prompt by name."""
        result = await self._send("prompts/get", {
            "name": name,
            "arguments": arguments or {},
        })
        return result

    async def close(self) -> None:
        """Close the connection."""
        if self._transport:
            await self._transport.close()
            self._transport = None
        self._initialized = False


class MCPClientError(Exception):
    """Raised when the MCP client encounters an error."""


# ======================================================================
# Transport layer
# ======================================================================


class _Transport:
    """Abstract transport."""

    async def send(self, message: dict[str, Any], *, timeout: float = 30.0) -> dict[str, Any]:
        raise NotImplementedError

    async def send_notification(self, message: dict[str, Any]) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError


class _StdioTransport(_Transport):
    """Stdio transport — launches a subprocess and speaks JSON-RPC over stdin/stdout."""

    def __init__(self, process: asyncio.subprocess.Process) -> None:
        self._process = process

    async def send(self, message: dict[str, Any], *, timeout: float = 30.0) -> dict[str, Any]:
        line = json.dumps(message) + "\n"
        self._process.stdin.write(line.encode())  # type: ignore[union-attr]
        await self._process.stdin.drain()  # type: ignore[union-attr]
        raw = await asyncio.wait_for(
            self._process.stdout.readline(),  # type: ignore[union-attr]
            timeout=timeout,
        )
        return json.loads(raw.decode().strip())

    async def send_notification(self, message: dict[str, Any]) -> None:
        line = json.dumps(message) + "\n"
        self._process.stdin.write(line.encode())  # type: ignore[union-attr]
        await self._process.stdin.drain()  # type: ignore[union-attr]

    async def close(self) -> None:
        if self._process.returncode is None:
            self._process.terminate()
            await self._process.wait()


class _HTTPTransport(_Transport):
    """HTTP transport — sends JSON-RPC to ``/mcp`` endpoint."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._session: Any = None

    async def _get_session(self) -> Any:
        if self._session is None:
            try:
                import aiohttp

                self._session = aiohttp.ClientSession()
            except ImportError:
                raise MCPClientError(
                    "aiohttp is required for HTTP transport — pip install aiohttp"
                )
        return self._session

    async def send(self, message: dict[str, Any], *, timeout: float = 30.0) -> dict[str, Any]:
        session = await self._get_session()
        import aiohttp

        async with session.post(
            f"{self._base_url}/mcp",
            json=message,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            return await resp.json()

    async def send_notification(self, message: dict[str, Any]) -> None:
        session = await self._get_session()
        import aiohttp

        async with session.post(
            f"{self._base_url}/mcp",
            json=message,
            timeout=aiohttp.ClientTimeout(total=5),
        ):
            pass

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None


# ======================================================================
# Context managers
# ======================================================================


class _StdioContextManager:
    """Async context manager for stdio connections."""

    def __init__(self, command: list[str], config: MCPClientConfig | None) -> None:
        self._command = command
        self._config = config
        self._client: MCPClient | None = None

    async def __aenter__(self) -> MCPClient:
        proc = await asyncio.create_subprocess_exec(
            *self._command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        client = MCPClient(self._config)
        client._transport = _StdioTransport(proc)
        await client.initialize()
        self._client = client
        return client

    async def __aexit__(self, *exc: Any) -> None:
        if self._client:
            await self._client.close()


class _HTTPContextManager:
    """Async context manager for HTTP connections."""

    def __init__(self, base_url: str, config: MCPClientConfig | None) -> None:
        self._base_url = base_url
        self._config = config
        self._client: MCPClient | None = None

    async def __aenter__(self) -> MCPClient:
        client = MCPClient(self._config)
        client._transport = _HTTPTransport(self._base_url)
        await client.initialize()
        self._client = client
        return client

    async def __aexit__(self, *exc: Any) -> None:
        if self._client:
            await self._client.close()
