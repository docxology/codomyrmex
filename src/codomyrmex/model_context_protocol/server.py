"""
MCP Server Implementation

Complete MCP server with tool, resource, and prompt support.
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
    """Configuration for MCP server."""
    name: str = "codomyrmex-mcp-server"
    version: str = "1.0.0"
    transport: str = "stdio"  # "stdio" or "http"
    log_level: str = "INFO"


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

    # =========================================================================
    # Tool Management
    # =========================================================================

    def tool(
        self,
        name: str | None = None,
        description: str | None = None,
    ):
        """Decorator to register a tool."""
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

            schema = {
                "name": tool_name,
                "description": tool_desc,
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }

            self._tool_registry.register(tool_name, schema, func)
            return func

        return decorator

    def register_tool(
        self,
        name: str,
        schema: dict[str, Any],
        handler: Callable,
    ) -> None:
        """Register a tool manually."""
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
            "protocolVersion": "2024-11-05",
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
        """Execute a tool."""
        tool_call = MCPToolCall(
            tool_name=params.get("name"),
            arguments=params.get("arguments", {}),
        )

        result = self._tool_registry.execute(tool_call)

        if result.status == "success":
            content = [{"type": "text", "text": json.dumps(result.data)}]
            return {"content": content}
        else:
            content = [{"type": "text", "text": result.error.error_message if result.error else "Unknown error"}]
            return {"content": content, "isError": True}

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

    def run(self) -> None:
        """Run the server."""
        asyncio.run(self.run_stdio())


__all__ = [
    "MCPServerConfig",
    "MCPServer",
]
