"""
MCP Server Implementation

Complete MCP server with tool, resource, and prompt support.
Supports both stdio and HTTP (Streamable HTTP + REST) transports.
"""

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from collections.abc import Callable

from .schemas.mcp_schemas import (
    MCPToolCall,
    MCPToolRegistry,
)


@dataclass
class MCPServerConfig:
    """Configuration for MCP server.

    Attributes:
        name: Server identity.
        version: Server version string.
        transport: Transport type ("stdio" or "http").
        log_level: Logging level.
        default_tool_timeout: Default per-tool execution timeout (seconds, 0 = no limit).
        per_tool_timeouts: Per-tool timeout overrides ``{tool_name: seconds}``.
        rate_limit_rate: Global rate limit (requests/second).
        rate_limit_burst: Global rate limit burst ceiling.
        warm_up: Eagerly populate discovery cache at server start.
    """
    name: str = "codomyrmex-mcp-server"
    version: str = "1.0.0"
    transport: str = "stdio"  # "stdio" or "http"
    log_level: str = "INFO"
    default_tool_timeout: float = 60.0
    per_tool_timeouts: dict[str, float] | None = None
    rate_limit_rate: float = 50.0
    rate_limit_burst: int = 100
    warm_up: bool = True


class MCPServer:
    """
    Full MCP server implementation.

    Supports:
    - Tool registration and execution
    - Resource management
    - Prompt templates
    - JSON-RPC over stdio or HTTP
    """

    def __init__(self, config: MCPServerConfig | None = None):
        self.config = config or MCPServerConfig()
        self._tool_registry = MCPToolRegistry()
        self._resources: dict[str, dict[str, Any]] = {}
        self._prompts: dict[str, dict[str, Any]] = {}
        self._initialized = False
        self._request_id = 0

        # Rate limiter
        from .rate_limiter import RateLimiter, RateLimiterConfig
        self._rate_limiter = RateLimiter(RateLimiterConfig(
            rate=self.config.rate_limit_rate,
            burst=self.config.rate_limit_burst,
        ))

    # =========================================================================
    # Tool Management
    # =========================================================================

    def tool(
        self,
        name: str | None = None,
        description: str | None = None,
        title: str | None = None,
        output_schema: dict[str, Any] | None = None,
    ):
        """Decorator to register a tool.

        Args:
            name: Programmatic tool name (used in tool calls).
            description: Tool description for the model.
            title: Human-friendly display name (MCP 2025-06-18).
            output_schema: JSON Schema for structured output (MCP 2025-06-18).
        """
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            tool_desc = description or func.__doc__ or ""

            # Build schema from function
            import inspect
            from typing import get_type_hints

            sig = inspect.signature(func)
            hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}

            properties = {}
            required = []
            type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}

            for pname, param in sig.parameters.items():
                if pname in ('self', 'cls'):
                    continue

                ptype = hints.get(pname, str)
                properties[pname] = {
                    "type": type_map.get(ptype, "string"),
                    "description": f"{pname} parameter",
                }
                if param.default == inspect.Parameter.empty:
                    required.append(pname)

            schema: dict[str, Any] = {
                "name": tool_name,
                "description": tool_desc,
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }

            # MCP 2025-06-18: human-friendly display name
            if title:
                schema["title"] = title

            # MCP 2025-06-18: structured output schema
            if output_schema:
                schema["outputSchema"] = output_schema

            self._tool_registry.register(tool_name, schema, func)
            return func

        return decorator

    def register_tool(
        self,
        name: str,
        schema: dict[str, Any],
        handler: Callable,
        title: str | None = None,
        output_schema: dict[str, Any] | None = None,
    ) -> None:
        """Register a tool manually.

        Args:
            name: Programmatic tool name.
            schema: Tool schema dict with name, description, inputSchema.
            handler: Callable that implements the tool.
            title: Human-friendly display name (MCP 2025-06-18).
            output_schema: JSON Schema for structured output (MCP 2025-06-18).
        """
        if title:
            schema["title"] = title
        if output_schema:
            schema["outputSchema"] = output_schema
        self._tool_registry.register(name, schema, handler)

    # =========================================================================
    # Resource Management
    # =========================================================================

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str | None = None,
        mime_type: str = "text/plain",
        content_provider: Callable[[], str] | None = None,
    ) -> None:
        """Register a resource."""
        self._resources[uri] = {
            "uri": uri,
            "name": name,
            "description": description,
            "mimeType": mime_type,
            "provider": content_provider,
        }

    def register_file_resource(self, path: str) -> None:
        """Register a file as a resource."""
        p = Path(path)

        def read_file():
            return p.read_text()

        mime_types = {
            ".txt": "text/plain",
            ".json": "application/json",
            ".md": "text/markdown",
            ".py": "text/x-python",
        }

        self.register_resource(
            uri=f"file://{p.absolute()}",
            name=p.name,
            description=f"File: {p.name}",
            mime_type=mime_types.get(p.suffix, "text/plain"),
            content_provider=read_file,
        )

    # =========================================================================
    # Prompt Management
    # =========================================================================

    def register_prompt(
        self,
        name: str,
        description: str | None = None,
        arguments: list[dict[str, Any]] | None = None,
        template: str | None = None,
    ) -> None:
        """Register a prompt template."""
        self._prompts[name] = {
            "name": name,
            "description": description,
            "arguments": arguments or [],
            "template": template,
        }

    # =========================================================================
    # Request Handling
    # =========================================================================

    async def handle_request(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Handle incoming JSON-RPC message."""
        method = message.get("method", "")
        params = message.get("params", {})
        request_id = message.get("id")

        # Notifications have no id
        if request_id is None:
            await self._handle_notification(method, params)
            return None

        try:
            result = await self._dispatch(method, params)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result,
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e),
                }
            }

    async def _handle_notification(self, method: str, params: dict[str, Any]) -> None:
        """Handle notifications."""
        if method == "notifications/initialized":
            self._initialized = True

    async def _dispatch(self, method: str, params: dict[str, Any]) -> Any:
        """Dispatch method call."""
        handlers = {
            "initialize": self._initialize,
            "tools/list": self._list_tools,
            "tools/call": self._call_tool,
            "resources/list": self._list_resources,
            "resources/read": self._read_resource,
            "prompts/list": self._list_prompts,
            "prompts/get": self._get_prompt,
        }

        handler = handlers.get(method)
        if not handler:
            raise ValueError(f"Unknown method: {method}")

        return await handler(params)

    async def _initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle initialize."""
        capabilities = {}
        if self._tool_registry.list_tools():
            capabilities["tools"] = {}
        if self._resources:
            capabilities["resources"] = {}
        if self._prompts:
            capabilities["prompts"] = {}

        return {
            "protocolVersion": "2025-06-18",
            "capabilities": capabilities,
            "serverInfo": {
                "name": self.config.name,
                "version": self.config.version,
            }
        }

    async def _list_tools(self, params: dict[str, Any]) -> dict[str, Any]:
        """List available tools."""
        tools = []
        for name in self._tool_registry.list_tools():
            tool = self._tool_registry.get(name)
            if tool:
                tools.append(tool["schema"])
        return {"tools": tools}

    async def _call_tool(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool.

        Validates arguments against the tool's ``inputSchema`` before dispatch.
        Returns a structured ``MCPToolError`` on validation failure.

        MCP 2025-06-18: When a tool defines an outputSchema, the response
        includes a 'structuredContent' field with the typed return value
        alongside the standard 'content' array.
        """
        from .validation import validate_tool_arguments
        from .errors import (
            MCPToolError,
            MCPErrorCode,
            FieldError,
            not_found_error,
            validation_error,
            execution_error,
        )

        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        # ── Look up the tool ──────────────────────────────────────────
        tool_entry = self._tool_registry.get(tool_name) if tool_name else None
        if not tool_entry:
            return not_found_error(tool_name).to_mcp_response()

        # ── Rate-limit check ──────────────────────────────────────────
        if not self._rate_limiter.allow(tool_name):
            return MCPToolError(
                code=MCPErrorCode.RATE_LIMITED,
                message=f"Rate limit exceeded for tool {tool_name!r}",
                tool_name=tool_name,
            ).to_mcp_response()

        # ── Validate arguments against inputSchema ────────────────────
        tool_schema = tool_entry.get("schema", {})
        vr = validate_tool_arguments(tool_name, arguments, tool_schema)

        if not vr.valid:
            field_errors = [
                FieldError(field=e.split(":")[0].strip(), constraint=e)
                for e in vr.errors
            ]
            return validation_error(
                tool_name=tool_name,
                message=f"Validation failed for tool {tool_name!r}: {'; '.join(vr.errors)}",
                field_errors=field_errors,
            ).to_mcp_response()

        # ── Compute per-tool timeout ──────────────────────────────────
        tool_timeout = self.config.default_tool_timeout
        if self.config.per_tool_timeouts and tool_name in self.config.per_tool_timeouts:
            tool_timeout = self.config.per_tool_timeouts[tool_name]

        # ── Execute with validated (and possibly coerced) arguments ───
        tool_call = MCPToolCall(
            tool_name=tool_name,
            arguments=vr.coerced_args,
        )

        try:
            if tool_timeout > 0:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, self._tool_registry.execute, tool_call
                    ),
                    timeout=tool_timeout,
                )
            else:
                result = self._tool_registry.execute(tool_call)
        except asyncio.TimeoutError:
            return MCPToolError(
                code=MCPErrorCode.TIMEOUT,
                message=f"Tool {tool_name!r} timed out after {tool_timeout}s",
                tool_name=tool_name,
            ).to_mcp_response()
        except Exception as exc:
            return execution_error(tool_name, exc).to_mcp_response()

        if result.status == "success":
            content = [{"type": "text", "text": json.dumps(result.data)}]
            response: dict[str, Any] = {"content": content}

            # MCP 2025-06-18: Include structuredContent when outputSchema exists
            if "outputSchema" in tool_schema:
                response["structuredContent"] = result.data

            return response
        else:
            # Wrap legacy MCPToolResult errors in structured envelope
            err_msg = result.error.error_message if result.error else "Unknown error"
            err_type = result.error.error_type if result.error else "Unknown"
            return MCPToolError(
                code=MCPErrorCode.EXECUTION_ERROR,
                message=err_msg,
                tool_name=tool_name,
                module=err_type,
            ).to_mcp_response()

    async def _list_resources(self, params: dict[str, Any]) -> dict[str, Any]:
        """List available resources."""
        resources = []
        for r in self._resources.values():
            resources.append({
                "uri": r["uri"],
                "name": r["name"],
                "description": r.get("description"),
                "mimeType": r.get("mimeType", "text/plain"),
            })
        return {"resources": resources}

    async def _read_resource(self, params: dict[str, Any]) -> dict[str, Any]:
        """Read a resource."""
        uri = params.get("uri")

        if uri not in self._resources:
            raise ValueError(f"Resource not found: {uri}")

        resource = self._resources[uri]
        provider = resource.get("provider")

        content = provider() if provider else ""

        return {
            "contents": [{
                "uri": uri,
                "mimeType": resource.get("mimeType", "text/plain"),
                "text": content,
            }]
        }

    async def _list_prompts(self, params: dict[str, Any]) -> dict[str, Any]:
        """List available prompts."""
        prompts = []
        for p in self._prompts.values():
            prompts.append({
                "name": p["name"],
                "description": p.get("description"),
                "arguments": p.get("arguments", []),
            })
        return {"prompts": prompts}

    async def _get_prompt(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get a prompt."""
        name = params.get("name")
        args = params.get("arguments", {})

        if name not in self._prompts:
            raise ValueError(f"Prompt not found: {name}")

        prompt = self._prompts[name]
        template = prompt.get("template", "")

        # Simple template substitution
        content = template
        for key, value in args.items():
            content = content.replace(f"{{{key}}}", str(value))

        return {
            "description": prompt.get("description"),
            "messages": [{
                "role": "user",
                "content": {"type": "text", "text": content}
            }]
        }

    # =========================================================================
    # Server Running
    # =========================================================================

    async def run_stdio(self) -> None:
        """Run server over stdio transport."""
        import sys

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break

                message = json.loads(line.strip())
                response = await self.handle_request(message)

                if response:
                    output = json.dumps(response)
                    print(output, flush=True)

            except json.JSONDecodeError:
                continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)

    async def run_http(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Run server over HTTP transport with Streamable HTTP + REST endpoints.

        Args:
            host: Bind address.
            port: Port number.
        """
        from fastapi import FastAPI, Request
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import HTMLResponse, JSONResponse
        import uvicorn

        from .web_ui import get_web_ui_html

        app = FastAPI(
            title=self.config.name,
            version=self.config.version,
            docs_url=None,
            redoc_url=None,
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        server = self  # capture for closures

        # --- Web UI ---
        @app.get("/", response_class=HTMLResponse)
        async def web_ui():
            return get_web_ui_html()

        # --- Health check ---
        @app.get("/health")
        async def health():
            return {
                "status": "ok",
                "server_name": server.config.name,
                "server_version": server.config.version,
                "protocol_version": "2025-06-18",
                "transport": "http",
                "tool_count": len(server._tool_registry.list_tools()),
                "resource_count": len(server._resources),
                "prompt_count": len(server._prompts),
            }

        # --- MCP JSON-RPC endpoint (Streamable HTTP) ---
        @app.post("/mcp")
        async def mcp_endpoint(request: Request):
            body = await request.json()
            response = await server.handle_request(body)
            if response is None:
                return JSONResponse(content={"status": "accepted"}, status_code=202)
            return JSONResponse(content=response)

        # --- Convenience REST endpoints ---
        @app.get("/tools")
        async def list_tools():
            result = await server._list_tools({})
            return JSONResponse(content=result)

        @app.get("/tools/{tool_name}")
        async def get_tool(tool_name: str):
            tool = server._tool_registry.get(tool_name)
            if not tool:
                return JSONResponse(
                    content={"error": f"Tool not found: {tool_name}"},
                    status_code=404,
                )
            return JSONResponse(content=tool["schema"])

        @app.post("/tools/{tool_name}/call")
        async def call_tool(tool_name: str, request: Request):
            try:
                body = await request.json()
            except Exception:
                body = {}
            result = await server._call_tool({
                "name": tool_name,
                "arguments": body,
            })
            return JSONResponse(content=result)

        @app.get("/resources")
        async def list_resources():
            result = await server._list_resources({})
            return JSONResponse(content=result)

        @app.get("/prompts")
        async def list_prompts():
            result = await server._list_prompts({})
            return JSONResponse(content=result)

        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level=self.config.log_level.lower(),
        )
        uv_server = uvicorn.Server(config)
        await uv_server.serve()

    def run(self) -> None:
        """Run the server."""
        asyncio.run(self.run_stdio())


__all__ = [
    "MCPServerConfig",
    "MCPServer",
]
