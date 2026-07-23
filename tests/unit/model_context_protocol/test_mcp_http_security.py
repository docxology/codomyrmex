"""Security contracts for the MCP HTTP application boundary."""

from __future__ import annotations

import httpx
import pytest

from codomyrmex.model_context_protocol.transport.server import MCPServer


def _server() -> MCPServer:
    server = MCPServer()

    @server.tool(name="read_only_probe", description="A harmless test probe")
    def read_only_probe() -> str:
        return "ok"

    return server


@pytest.mark.asyncio
async def test_http_app_requires_bearer_auth_when_configured() -> None:
    app = _server()._create_http_app(
        allowed_origins=["https://trusted.example"],
        auth_token="secret",
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        unauthenticated = await client.get("/health")
        authenticated = await client.get(
            "/health",
            headers={
                "Authorization": "Bearer secret",
                "Origin": "https://trusted.example",
            },
        )

    assert unauthenticated.status_code == 401
    assert authenticated.status_code == 200
    assert (
        authenticated.headers["access-control-allow-origin"]
        == "https://trusted.example"
    )


@pytest.mark.asyncio
async def test_http_app_does_not_grant_unconfigured_origin() -> None:
    app = _server()._create_http_app(
        allowed_origins=["https://trusted.example"],
        auth_token="secret",
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get(
            "/health",
            headers={
                "Authorization": "Bearer secret",
                "Origin": "https://untrusted.example",
            },
        )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_http_app_rejects_wildcard_cors() -> None:
    with pytest.raises(ValueError, match="wildcard CORS"):
        _server()._create_http_app(allowed_origins=["*"])


@pytest.mark.asyncio
async def test_non_loopback_http_requires_authentication() -> None:
    with pytest.raises(ValueError, match="auth_token is required"):
        await _server().run_http(host="0.0.0.0", port=0)
