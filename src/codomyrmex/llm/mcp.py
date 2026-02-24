"""
MCP Integration for LLM Module

Provides a bridge between the LLM tool calling framework and the Model Context Protocol.
"""

import asyncio
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from collections.abc import Callable


class MCPCapability(Enum):
    """MCP server capabilities."""
    TOOLS = "tools"
    RESOURCES = "resources"
    PROMPTS = "prompts"
    LOGGING = "logging"


@dataclass
class MCPClientInfo:
    """Client information for MCP handshake."""
    name: str
    version: str = "1.0.0"


@dataclass
class MCPServerInfo:
    """Server information for MCP handshake."""
    name: str
    version: str = "1.0.0"
    capabilities: dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPResource:
    """An MCP resource (context data)."""
    uri: str
    name: str
    description: str | None = None
    mime_type: str = "text/plain"


@dataclass
class MCPPrompt:
    """An MCP prompt template."""
    name: str
    description: str | None = None
    arguments: list[dict[str, Any]] = field(default_factory=list)


class MCPBridge:
    """
    Bridge between Codomyrmex LLM tools and MCP protocol.

    Converts between native Tool format and MCP JSON-RPC format.
    Supports both client and server modes.
    """

    def __init__(
        self,
        server_info: MCPServerInfo | None = None,
        client_info: MCPClientInfo | None = None,
    ):
        """Execute   Init   operations natively."""
        self.server_info = server_info or MCPServerInfo(name="codomyrmex-mcp")
        self.client_info = client_info or MCPClientInfo(name="codomyrmex-client")

        self._tools: dict[str, dict[str, Any]] = {}
        self._resources: dict[str, MCPResource] = {}
        self._prompts: dict[str, MCPPrompt] = {}
        self._handlers: dict[str, Callable] = {}
        self._initialized = False
        self._request_id = 0

    def _next_request_id(self) -> int:
        """Generate next request ID."""
        self._request_id += 1
        return self._request_id

    # =========================================================================
    # Tool Registration
    # =========================================================================

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable,
    ) -> None:
        """Register a tool with MCP bridge."""
        self._tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
        }
        self._handlers[name] = handler

    def register_tool_from_function(
        self,
        func: Callable,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        """Register a tool from a Python function (auto-generates schema)."""
        import inspect
        from typing import get_type_hints

        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or f"Tool: {tool_name}"

        # Build input schema from function signature
        sig = inspect.signature(func)
        type_hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}

        properties = {}
        required = []

        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue

            python_type = type_hints.get(param_name, str)
            json_type = type_map.get(python_type, "string")

            properties[param_name] = {
                "type": json_type,
                "description": f"Parameter: {param_name}",
            }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        input_schema = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

        self.register_tool(tool_name, tool_desc, input_schema, func)

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools in MCP format."""
        return list(self._tools.values())

    # =========================================================================
    # Resource Registration
    # =========================================================================

    def register_resource(self, resource: MCPResource) -> None:
        """Register a resource."""
        self._resources[resource.uri] = resource

    def list_resources(self) -> list[dict[str, Any]]:
        """List all registered resources."""
        return [
            {
                "uri": r.uri,
                "name": r.name,
                "description": r.description,
                "mimeType": r.mime_type,
            }
            for r in self._resources.values()
        ]

    # =========================================================================
    # Prompt Registration
    # =========================================================================

    def register_prompt(self, prompt: MCPPrompt) -> None:
        """Register a prompt template."""
        self._prompts[prompt.name] = prompt

    def list_prompts(self) -> list[dict[str, Any]]:
        """List all registered prompts."""
        return [
            {
                "name": p.name,
                "description": p.description,
                "arguments": p.arguments,
            }
            for p in self._prompts.values()
        ]

    # =========================================================================
    # JSON-RPC Message Handling
    # =========================================================================

    def create_request(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a JSON-RPC request."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": method,
        }
        if params:
            request["params"] = params
        return request

    def create_response(
        self,
        request_id: int | str,
        result: Any = None,
        error: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a JSON-RPC response."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
        }
        if error:
            response["error"] = error
        else:
            response["result"] = result
        return response

    def create_notification(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a JSON-RPC notification (no id)."""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params:
            notification["params"] = params
        return notification

    async def handle_request(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Handle an incoming JSON-RPC request."""
        method = message.get("method", "")
        params = message.get("params", {})
        request_id = message.get("id")

        # Notifications don't have id and don't expect response
        if request_id is None:
            await self._handle_notification(method, params)
            return None

        try:
            result = await self._dispatch_method(method, params)
            return self.create_response(request_id, result=result)
        except Exception as e:
            return self.create_response(
                request_id,
                error={
                    "code": -32603,
                    "message": str(e),
                }
            )

    async def _handle_notification(self, method: str, params: dict[str, Any]) -> None:
        """Handle a notification."""
        if method == "notifications/initialized":
            self._initialized = True
        elif method == "notifications/cancelled":
            pass  # Handle request cancellation

    async def _dispatch_method(self, method: str, params: dict[str, Any]) -> Any:
        """Dispatch a method call."""
        if method == "initialize":
            return await self._handle_initialize(params)
        elif method == "tools/list":
            return {"tools": self.list_tools()}
        elif method == "tools/call":
            return await self._handle_tool_call(params)
        elif method == "resources/list":
            return {"resources": self.list_resources()}
        elif method == "resources/read":
            return await self._handle_resource_read(params)
        elif method == "prompts/list":
            return {"prompts": self.list_prompts()}
        elif method == "prompts/get":
            return await self._handle_prompt_get(params)
        else:
            raise ValueError(f"Unknown method: {method}")

    async def _handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle initialize request."""
        client_info = params.get("clientInfo", {})

        # Build capabilities based on what's registered
        capabilities = {}
        if self._tools:
            capabilities["tools"] = {}
        if self._resources:
            capabilities["resources"] = {}
        if self._prompts:
            capabilities["prompts"] = {}

        return {
            "protocolVersion": "2024-11-05",
            "capabilities": capabilities,
            "serverInfo": {
                "name": self.server_info.name,
                "version": self.server_info.version,
            },
        }

    async def _handle_tool_call(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle a tool call."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self._handlers:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: Tool '{tool_name}' not found",
                }],
                "isError": True,
            }

        try:
            handler = self._handlers[tool_name]
            result = handler(**arguments)

            if asyncio.iscoroutine(result):
                result = await result

            # Format result as MCP content
            if isinstance(result, str):
                content = [{"type": "text", "text": result}]
            elif isinstance(result, dict):
                content = [{"type": "text", "text": json.dumps(result, indent=2)}]
            else:
                content = [{"type": "text", "text": str(result)}]

            return {"content": content}
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {e}"}],
                "isError": True,
            }

    async def _handle_resource_read(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle resource read."""
        uri = params.get("uri")

        if uri not in self._resources:
            raise ValueError(f"Resource not found: {uri}")

        resource = self._resources[uri]

        raise NotImplementedError("MCP resource read not yet implemented for this resource type")

    async def _handle_prompt_get(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle prompt get."""
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name not in self._prompts:
            raise ValueError(f"Prompt not found: {name}")

        prompt = self._prompts[name]

        return {
            "description": prompt.description,
            "messages": [{
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Prompt: {prompt.name}",
                }
            }]
        }

    # =========================================================================
    # stdio Transport
    # =========================================================================

    async def run_stdio(self) -> None:
        """Run as stdio-based MCP server."""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break

                message = json.loads(line)
                response = await self.handle_request(message)

                if response:
                    # Write response to stdout
                    print(json.dumps(response), file=sys.stdout, flush=True)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)


# =========================================================================
# Integration with LLM Tools
# =========================================================================

def convert_tool_to_mcp(tool) -> dict[str, Any]:
    """Convert a codomyrmex.llm.tools.Tool to MCP format."""
    properties = {}
    required = []

    for param in tool.parameters:
        properties[param.name] = param.to_json_schema()
        if param.required:
            required.append(param.name)

    return {
        "name": tool.name,
        "description": tool.description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required,
        }
    }


def create_mcp_bridge_from_registry(registry) -> MCPBridge:
    """Create an MCPBridge from an LLM ToolRegistry."""
    bridge = MCPBridge()

    for tool in registry.list_tools():
        mcp_tool = convert_tool_to_mcp(tool)
        bridge.register_tool(
            name=tool.name,
            description=tool.description,
            input_schema=mcp_tool["inputSchema"],
            handler=tool.function,
        )

    return bridge


__all__ = [
    "MCPCapability",
    "MCPClientInfo",
    "MCPServerInfo",
    "MCPResource",
    "MCPPrompt",
    "MCPBridge",
    "convert_tool_to_mcp",
    "create_mcp_bridge_from_registry",
]
