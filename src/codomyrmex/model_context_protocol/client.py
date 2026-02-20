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
import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class MCPClientConfig:
    """Configuration for an MCP client connection.

    Attributes:
        name: Client identity name.
        version: Client version string.
        timeout_seconds: Default per-request timeout.
        protocol_version: MCP protocol version to negotiate.
        max_retries: Max retry attempts for transient errors.
        retry_delay: Base delay (seconds) between retries (doubled each attempt).
        health_check_interval: Seconds between health pings (0 = disabled).
        connection_pool_size: Max simultaneous HTTP connections.
    """

    name: str = "codomyrmex-mcp-client"
    version: str = "0.1.0"
    timeout_seconds: float = 30.0
    protocol_version: str = "2025-06-18"
    max_retries: int = 3
    retry_delay: float = 0.5
    health_check_interval: float = 0.0
    connection_pool_size: int = 10


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

    async def _send(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Send a JSON-RPC request with automatic retry.

        Retries on ``asyncio.TimeoutError``, ``OSError``, and
        ``ConnectionError`` up to ``config.max_retries`` times with
        exponential back-off.
        """
        msg: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {},
        }
        assert self._transport is not None, "Not connected — use a context manager"
        effective_timeout = timeout or self.config.timeout_seconds
        last_exc: Exception | None = None

        for attempt in range(1, self.config.max_retries + 1):
            try:
                response = await self._transport.send(msg, timeout=effective_timeout)
                if "error" in response:
                    raise MCPClientError(
                        f"RPC error on {method}: {response['error'].get('message', response['error'])}"
                    )
                return response.get("result", {})
            except (asyncio.TimeoutError, OSError, ConnectionError) as exc:
                last_exc = exc
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (2 ** (attempt - 1))
                    logger.warning(
                        "MCP request %s attempt %d/%d failed (%s), retrying in %.1fs",
                        method, attempt, self.config.max_retries, exc, delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "MCP request %s failed after %d attempts: %s",
                        method, self.config.max_retries, exc,
                    )
        raise MCPClientError(
            f"Request {method} failed after {self.config.max_retries} retries: {last_exc}"
        )

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

    async def health_check(self) -> dict[str, Any]:
        """Ping the server and return latency + status.

        Returns::

            {"ok": True, "latency_ms": 12.3, "server": ...}

        Raises:
            MCPClientError: If the server is unreachable.
        """
        t0 = time.monotonic()
        try:
            result = await self._send("ping", timeout=5.0)
            latency = (time.monotonic() - t0) * 1000
            return {"ok": True, "latency_ms": round(latency, 2), "server": self._server_info}
        except MCPClientError:
            # Many servers don't implement ping — fall back to tools/list
            try:
                await self._send("tools/list", timeout=5.0)
                latency = (time.monotonic() - t0) * 1000
                return {"ok": True, "latency_ms": round(latency, 2), "server": self._server_info}
            except Exception as exc:
                latency = (time.monotonic() - t0) * 1000
                return {"ok": False, "latency_ms": round(latency, 2), "error": str(exc)}

    async def list_tools(self) -> list[dict[str, Any]]:
        """List tools exposed by the server."""
        result = await self._send("tools/list")
        return result.get("tools", [])

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Invoke a tool on the server.

        Args:
            name: Tool name.
            arguments: Tool arguments dict.
            timeout: Optional per-call timeout override.

        Returns:
            The tool result dict.  If the server returned a structured
            ``MCPToolError``, it is available under the ``"_error"`` key.
        """
        result = await self._send(
            "tools/call",
            {"name": name, "arguments": arguments or {}},
            timeout=timeout,
        )

        # Parse structured MCPToolError from server response
        if result.get("isError"):
            try:
                from .errors import MCPToolError as _MCPToolError
                content_text = result.get("content", [{}])[0].get("text", "")
                parsed = _MCPToolError.from_json(content_text)
                if parsed:
                    result["_error"] = parsed
            except Exception:
                pass  # leave unstructured

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
    """HTTP transport — sends JSON-RPC to ``/mcp`` endpoint.

    Supports connection pooling via ``pool_size`` parameter.
    """

    def __init__(self, base_url: str, *, pool_size: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._pool_size = pool_size
        self._session: Any = None

    async def _get_session(self) -> Any:
        if self._session is None:
            try:
                import aiohttp

                connector = aiohttp.TCPConnector(
                    limit=self._pool_size,
                    enable_cleanup_closed=True,
                )
                self._session = aiohttp.ClientSession(connector=connector)
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
        cfg = self._config or MCPClientConfig()
        client = MCPClient(cfg)
        client._transport = _HTTPTransport(
            self._base_url,
            pool_size=cfg.connection_pool_size,
        )
        await client.initialize()
        self._client = client
        return client

    async def __aexit__(self, *exc: Any) -> None:
        if self._client:
            await self._client.close()
