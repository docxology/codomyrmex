"""Tests for MCP server: JSON-RPC handling, HTTP endpoints, tool wiring, and discovery."""

import asyncio
import json
import sys
from pathlib import Path

import pytest

pydantic = pytest.importorskip("pydantic")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


def _make_server(code_dir):
    """Create a fully-configured MCP server (same as run_mcp_server.create_server)."""
    if str(code_dir) not in sys.path:
        sys.path.insert(0, str(code_dir))

    # Import here so path is set up
    from scripts_helper import create_server
    return create_server()


def _import_create_server(code_dir):
    """Import create_server from the runner script."""
    if str(code_dir) not in sys.path:
        sys.path.insert(0, str(code_dir))

    project_root = Path(code_dir).parent
    scripts_dir = project_root / "scripts" / "model_context_protocol"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    # We can also just import directly through the source
    from codomyrmex.model_context_protocol.transport.server import (
        MCPServer,
        MCPServerConfig,
    )
    return MCPServer, MCPServerConfig


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def server(code_dir):
    """Create a minimal MCP server with built-in tools wired to tools.py."""
    if str(code_dir) not in sys.path:
        sys.path.insert(0, str(code_dir))

    from codomyrmex.model_context_protocol import tools as mcp_tools
    from codomyrmex.model_context_protocol.transport.server import (
        MCPServer,
        MCPServerConfig,
    )

    config = MCPServerConfig(name="test-mcp", version="0.1.0")
    srv = MCPServer(config)

    # Register a few tools that delegate to tools.py
    @srv.tool(name="read_file", title="Read File", description="Read file contents")
    def read_file(path: str, encoding: str = "utf-8") -> str:
        return json.dumps(mcp_tools.read_file(path=path, encoding=encoding))

    @srv.tool(name="git_status", title="Git Status", description="Git repo status")
    def git_status(path: str = ".") -> str:
        return json.dumps(mcp_tools.git_status(path=path))

    @srv.tool(name="checksum_file", title="Checksum", description="File checksum")
    def checksum_file(path: str, algorithm: str = "sha256") -> str:
        return json.dumps(mcp_tools.checksum_file(path=path, algorithm=algorithm))

    @srv.tool(name="json_query", title="JSON Query", description="Query JSON files")
    def json_query(path: str, query: str = "") -> str:
        return json.dumps(mcp_tools.json_query(path=path, query=query or None))

    @srv.tool(name="analyze_python_file", title="Analyze Python", description="Analyze .py")
    def analyze_python_file(path: str) -> str:
        return json.dumps(mcp_tools.analyze_python_file(path=path))

    # Register a resource and prompt for completeness
    srv.register_resource(
        uri="test://readme",
        name="Test README",
        description="Test resource",
        content_provider=lambda: "Hello from test resource",
    )
    srv.register_prompt(
        name="test_prompt",
        description="A test prompt",
        template="Say {greeting} to {name}",
        arguments=[
            {"name": "greeting", "description": "The greeting"},
            {"name": "name", "description": "Who to greet"},
        ],
    )

    return srv


@pytest.fixture
def mock_client(server):
    """TestMCPClient wrapping the test server."""
    if str(Path(__file__).resolve().parents[3]) not in sys.path:
        sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

    from codomyrmex.model_context_protocol.quality.testing import TestMCPClient
    return TestMCPClient(server)


# ---------------------------------------------------------------------------
# JSON-RPC Protocol Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMCPProtocol:
    """Test core JSON-RPC MCP protocol handling."""

    def test_initialize_handshake(self, server):
        """Test functionality: initialize handshake."""
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "pytest", "version": "1.0"},
            },
        }))
        assert resp is not None
        assert "result" in resp
        result = resp["result"]
        assert result["protocolVersion"] == "2025-06-18"
        assert "tools" in result["capabilities"]
        assert "resources" in result["capabilities"]
        assert "prompts" in result["capabilities"]
        assert result["serverInfo"]["name"] == "test-mcp"

    def test_notification_no_response(self, server):
        """Test functionality: notification no response."""
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }))
        assert resp is None

    def test_unknown_method_returns_error(self, server):
        """Test functionality: unknown method returns error."""
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 99,
            "method": "nonexistent/method",
            "params": {},
        }))
        assert "error" in resp
        assert resp["error"]["code"] == -32603

    def test_tools_list(self, server):
        """Test functionality: tools list."""
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }))
        tools = resp["result"]["tools"]
        names = [t["name"] for t in tools]
        assert "read_file" in names
        assert "git_status" in names
        assert "checksum_file" in names
        assert "json_query" in names
        assert "analyze_python_file" in names

    def test_resources_list(self, server):
        """Test functionality: resources list."""
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/list",
            "params": {},
        }))
        resources = resp["result"]["resources"]
        assert len(resources) >= 1
        assert resources[0]["uri"] == "test://readme"

    def test_resources_read(self, server):
        """Test functionality: resources read."""
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/read",
            "params": {"uri": "test://readme"},
        }))
        contents = resp["result"]["contents"]
        assert contents[0]["text"] == "Hello from test resource"

    def test_prompts_list(self, server):
        """Test functionality: prompts list."""
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "prompts/list",
            "params": {},
        }))
        prompts = resp["result"]["prompts"]
        assert any(p["name"] == "test_prompt" for p in prompts)

    def test_prompts_get(self, server):
        """Test functionality: prompts get."""
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "prompts/get",
            "params": {"name": "test_prompt", "arguments": {"greeting": "hello", "name": "world"}},
        }))
        messages = resp["result"]["messages"]
        assert "hello" in messages[0]["content"]["text"]
        assert "world" in messages[0]["content"]["text"]


# ---------------------------------------------------------------------------
# Tool Execution Tests (tools.py integration)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestToolExecution:
    """Test that built-in tools call tools.py and return structured results."""

    def test_read_file_success(self, server, tmp_path):
        """Test functionality: read file success."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {"name": "read_file", "arguments": {"path": str(test_file)}},
        }))
        result = resp["result"]
        assert "content" in result
        assert "isError" not in result
        data = json.loads(result["content"][0]["text"])
        inner = json.loads(data["result"])
        assert inner["success"] is True
        assert inner["content"] == "hello world"
        assert inner["lines"] == 1

    def test_read_file_not_found(self, server):
        """Test functionality: read file not found."""
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {"name": "read_file", "arguments": {"path": "/nonexistent/file.txt"}},
        }))
        result = resp["result"]
        data = json.loads(result["content"][0]["text"])
        inner = json.loads(data["result"])
        assert inner["success"] is False
        assert "error" in inner

    def test_git_status(self, server):
        """Test functionality: git status."""
        # Run in the project root (which is a git repo)
        project_root = Path(__file__).resolve().parents[5]
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {"name": "git_status", "arguments": {"path": str(project_root)}},
        }))
        result = resp["result"]
        data = json.loads(result["content"][0]["text"])
        inner = json.loads(data["result"])
        assert inner["success"] is True
        assert "branch" in inner

    def test_checksum_file(self, server, tmp_path):
        """Test functionality: checksum file."""
        test_file = tmp_path / "check.txt"
        test_file.write_text("checksum me")

        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {"name": "checksum_file", "arguments": {"path": str(test_file)}},
        }))
        result = resp["result"]
        data = json.loads(result["content"][0]["text"])
        inner = json.loads(data["result"])
        assert inner["success"] is True
        assert inner["algorithm"] == "sha256"
        assert len(inner["checksum"]) == 64  # sha256 hex length

    def test_json_query(self, server, tmp_path):
        """Test functionality: json query."""
        json_file = tmp_path / "data.json"
        json_file.write_text(json.dumps({"name": "test", "items": [1, 2, 3]}))

        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 14,
            "method": "tools/call",
            "params": {"name": "json_query", "arguments": {"path": str(json_file), "query": "name"}},
        }))
        result = resp["result"]
        data = json.loads(result["content"][0]["text"])
        inner = json.loads(data["result"])
        assert inner["success"] is True
        assert inner["result"] == "test"

    def test_analyze_python_file(self, server):
        """Test functionality: analyze python file."""
        # Analyze tools.py itself
        tools_py = Path(__file__).resolve().parents[3] / "model_context_protocol" / "tools.py"
        if not tools_py.exists():
            pytest.skip("tools.py not found")

        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 15,
            "method": "tools/call",
            "params": {"name": "analyze_python_file", "arguments": {"path": str(tools_py)}},
        }))
        result = resp["result"]
        data = json.loads(result["content"][0]["text"])
        inner = json.loads(data["result"])
        assert inner["success"] is True
        assert inner["metrics"]["function_count"] >= 5

    def test_unknown_tool_returns_error(self, server):
        """Test functionality: unknown tool returns error."""
        resp = _run(server.handle_request({
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {"name": "nonexistent_tool", "arguments": {}},
        }))
        result = resp["result"]
        assert result.get("isError") is True


# ---------------------------------------------------------------------------
# TestMCPClient Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMockClient:
    """Test the TestMCPClient from testing.py."""

    def test_client_initialize(self, mock_client):
        """Test functionality: client initialize."""
        resp = _run(mock_client.initialize())
        assert "result" in resp
        assert resp["result"]["protocolVersion"] == "2025-06-18"

    def test_client_list_tools(self, mock_client):
        """Test functionality: client list tools."""
        resp = _run(mock_client.list_tools())
        tools = resp["result"]["tools"]
        assert len(tools) >= 5

    def test_client_call_tool(self, mock_client, tmp_path):
        """Test functionality: client call tool."""
        f = tmp_path / "hello.txt"
        f.write_text("hi")
        resp = _run(mock_client.call_tool("read_file", {"path": str(f)}))
        assert "result" in resp
        assert "content" in resp["result"]

    def test_client_list_resources(self, mock_client):
        """Test functionality: client list resources."""
        resp = _run(mock_client.list_resources())
        assert "result" in resp
        assert len(resp["result"]["resources"]) >= 1


# ---------------------------------------------------------------------------
# ServerTester Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestServerTester:
    """Test the ServerTester smoke test framework."""

    def test_smoke_tests_pass(self, server, code_dir):
        """Test functionality: smoke tests pass."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.model_context_protocol.quality.testing import ServerTester
        tester = ServerTester(server)
        suite = _run(tester.run_smoke_tests())
        assert suite.passed >= 2
        assert suite.failed == 0


# ---------------------------------------------------------------------------
# HTTP Transport Tests (using FastAPI TestClient)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHTTPTransport:
    """Test the HTTP/REST endpoints via FastAPI TestClient."""

    @pytest.fixture
    def http_app(self, server):
        """Build a FastAPI app from the server's run_http internals."""
        try:
            from fastapi import FastAPI, Request
            from fastapi.middleware.cors import CORSMiddleware
            from fastapi.responses import HTMLResponse, JSONResponse
        except ImportError:
            pytest.skip("fastapi not installed")

        try:
            from codomyrmex.model_context_protocol.transport.web_ui import (
                get_web_ui_html,
            )
        except ImportError:
            pytest.skip("web_ui module not available")

        app = FastAPI(docs_url=None, redoc_url=None)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        srv = server

        @app.get("/", response_class=HTMLResponse)
        async def web_ui():
            return get_web_ui_html()

        @app.get("/health")
        async def health():
            return {
                "status": "ok",
                "server_name": srv.config.name,
                "server_version": srv.config.version,
                "protocol_version": "2025-06-18",
                "transport": "http",
                "tool_count": len(srv._tool_registry.list_tools()),
                "resource_count": len(srv._resources),
                "prompt_count": len(srv._prompts),
            }

        @app.post("/mcp")
        async def mcp_endpoint(request: Request):
            body = await request.json()
            response = await srv.handle_request(body)
            if response is None:
                return JSONResponse(content={"status": "accepted"}, status_code=202)
            return JSONResponse(content=response)

        @app.get("/tools")
        async def list_tools():
            result = await srv._list_tools({})
            return JSONResponse(content=result)

        @app.get("/tools/{tool_name}")
        async def get_tool(tool_name: str):
            tool = srv._tool_registry.get(tool_name)
            if not tool:
                return JSONResponse(content={"error": f"Tool not found: {tool_name}"}, status_code=404)
            return JSONResponse(content=tool["schema"])

        @app.post("/tools/{tool_name}/call")
        async def call_tool(tool_name: str, request: Request):
            try:
                body = await request.json()
            except Exception:
                body = {}
            result = await srv._call_tool({"name": tool_name, "arguments": body})
            return JSONResponse(content=result)

        @app.get("/resources")
        async def list_resources():
            result = await srv._list_resources({})
            return JSONResponse(content=result)

        @app.get("/prompts")
        async def list_prompts():
            result = await srv._list_prompts({})
            return JSONResponse(content=result)

        return app

    @pytest.fixture
    def client(self, http_app):
        try:
            from starlette.testclient import TestClient
        except ImportError:
            pytest.skip("starlette not installed")
        return TestClient(http_app)

    def test_health_endpoint(self, client):
        """Test functionality: health endpoint."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["server_name"] == "test-mcp"
        assert data["tool_count"] >= 5

    def test_web_ui_serves_html(self, client):
        """Test functionality: web ui serves html."""
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "Codomyrmex MCP Server" in resp.text

    def test_list_tools_endpoint(self, client):
        """Test functionality: list tools endpoint."""
        resp = client.get("/tools")
        assert resp.status_code == 200
        data = resp.json()
        assert "tools" in data
        names = [t["name"] for t in data["tools"]]
        assert "read_file" in names

    def test_get_tool_endpoint(self, client):
        """Test functionality: get tool endpoint."""
        resp = client.get("/tools/read_file")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "read_file"

    def test_get_tool_not_found(self, client):
        """Test functionality: get tool not found."""
        resp = client.get("/tools/no_such_tool")
        assert resp.status_code == 404

    def test_call_tool_endpoint(self, client, tmp_path):
        """Test functionality: call tool endpoint."""
        f = tmp_path / "http_test.txt"
        f.write_text("http test content")
        resp = client.post(
            "/tools/read_file/call",
            json={"path": str(f)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data

    def test_mcp_jsonrpc_endpoint(self, client):
        """Test functionality: mcp jsonrpc endpoint."""
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "tools" in data["result"]

    def test_mcp_notification_returns_202(self, client):
        """Test functionality: mcp notification returns 202."""
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        })
        assert resp.status_code == 202

    def test_resources_endpoint(self, client):
        """Test functionality: resources endpoint."""
        resp = client.get("/resources")
        assert resp.status_code == 200
        data = resp.json()
        assert "resources" in data

    def test_prompts_endpoint(self, client):
        """Test functionality: prompts endpoint."""
        resp = client.get("/prompts")
        assert resp.status_code == 200
        data = resp.json()
        assert "prompts" in data
