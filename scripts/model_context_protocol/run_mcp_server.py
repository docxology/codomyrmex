#!/usr/bin/env python3
"""
MCP Server Runner - Start an MCP server with Codomyrmex tools.

Usage:
    python run_mcp_server.py [--transport stdio|http] [--port 8080]

Examples:
    # Run stdio server for Claude Desktop
    python run_mcp_server.py --transport stdio

    # Run HTTP server for remote/browser access
    python run_mcp_server.py --transport http --port 8080

    # List available tools
    python run_mcp_server.py --list-tools
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import asyncio
import json
from typing import Any, Dict, List, Optional

from codomyrmex.model_context_protocol import MCPServer, MCPServerConfig
from codomyrmex.model_context_protocol.discovery import (
    DiscoveredTool,
    SpecificationScanner,
    ToolCatalog,
    discover_tools,
)
from codomyrmex.model_context_protocol import tools as mcp_tools
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


# ============================================================================
# Known tool-name -> tools.py function mapping for spec-discovered tools
# ============================================================================

_SPEC_TOOL_IMPLEMENTATIONS: Dict[str, Any] = {
    "git_status": mcp_tools.git_status,
    "git_diff": mcp_tools.git_diff,
    "read_file": mcp_tools.read_file,
    "write_file": mcp_tools.write_file,
    "list_directory": mcp_tools.list_directory,
    "search_code": mcp_tools.search_codebase,
    "search_codebase": mcp_tools.search_codebase,
    "run_command": mcp_tools.run_shell_command,
    "run_shell_command": mcp_tools.run_shell_command,
    "analyze_python_file": mcp_tools.analyze_python_file,
    "json_query": mcp_tools.json_query,
    "checksum_file": mcp_tools.checksum_file,
}


# ============================================================================
# MCP Tool Discovery Bridge
# ============================================================================

def discover_and_register_tools(server: MCPServer) -> int:
    """
    Discover tools from MCP_TOOL_SPECIFICATION.md files across all modules
    and register them with the MCP server.

    Returns the number of tools discovered and registered.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    modules_dir = project_root / "src" / "codomyrmex"

    # Find all MCP_TOOL_SPECIFICATION.md files
    spec_files = list(modules_dir.rglob("MCP_TOOL_SPECIFICATION.md"))
    logger.info(f"Found {len(spec_files)} MCP specification files")

    # Use the discovery system to scan specifications
    catalog = discover_tools(spec_files=spec_files)
    discovered = catalog.list_all()
    registered_count = 0

    for tool in discovered:
        # Skip tools with empty names or duplicates of built-in tools
        if not tool.name or not tool.name.strip():
            continue

        # Sanitize tool name: lowercase, replace spaces/special chars
        safe_name = tool.name.lower().replace(" ", "_").replace("-", "_")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c == "_")

        if not safe_name:
            continue

        # Prefix with module source to avoid collisions
        source_module = _extract_module_name(tool.source_path, str(modules_dir))
        if source_module:
            prefixed_name = f"{source_module}__{safe_name}"
        else:
            prefixed_name = safe_name

        # Check for duplicate tool names
        existing = server._tool_registry.list_tools()
        if prefixed_name in existing:
            continue

        # Build schema for registration (MCP 2025-06-18: includes title)
        # Check if this tool has a real implementation
        impl_func = _SPEC_TOOL_IMPLEMENTATIONS.get(safe_name)
        has_impl = impl_func is not None

        schema = {
            "name": prefixed_name,
            "title": tool.name,  # MCP 2025-06-18: human-friendly display name
            "description": tool.description or f"Discovered tool: {tool.name}",
            "inputSchema": tool.input_schema if tool.input_schema else {
                "type": "object",
                "properties": {},
                "required": [],
            },
            "_implementation_status": "fully_implemented" if has_impl else "spec_only",
        }

        if has_impl:
            # Wire to the actual tools.py implementation
            server.register_tool(prefixed_name, schema, impl_func)
        else:
            # Spec-only: return structured metadata about the tool
            def make_handler(t: DiscoveredTool):
                def handler(**kwargs):
                    return {
                        "status": "spec_only",
                        "tool_name": t.name,
                        "source": t.source_path,
                        "message": (
                            f"Tool '{t.name}' is defined in the MCP specification "
                            f"but does not have a direct implementation wired into "
                            f"the MCP server. To use this tool, invoke the underlying "
                            f"module code directly."
                        ),
                        "module": _extract_module_name(t.source_path, str(modules_dir)),
                        "provided_arguments": kwargs,
                    }
                return handler

            server.register_tool(prefixed_name, schema, make_handler(tool))

        registered_count += 1
        logger.debug(f"Registered discovered tool: {prefixed_name} ({'implemented' if has_impl else 'spec_only'})")

    logger.info(f"Registered {registered_count} discovered tools from specifications")
    return registered_count


def _extract_module_name(source_path: str, base_dir: str) -> str:
    """Extract the module name from a specification file path."""
    try:
        rel = Path(source_path).relative_to(base_dir)
        parts = rel.parts
        # The first directory component is the module name
        if parts:
            return parts[0]
    except (ValueError, IndexError):
        pass
    return ""


# ============================================================================
# Built-in Codomyrmex Tools (delegating to tools.py)
# ============================================================================

def create_file_tools(server: MCPServer) -> None:
    """Register file operation tools (delegating to tools.py)."""

    @server.tool(
        name="read_file",
        title="Read File",
        description="Read file contents with metadata including size, line count, and modification time",
    )
    def read_file(path: str, encoding: str = "utf-8") -> str:
        result = mcp_tools.read_file(path=path, encoding=encoding)
        return json.dumps(result)

    @server.tool(
        name="write_file",
        title="Write File",
        description="Write content to a file, creating parent directories if needed",
    )
    def write_file(path: str, content: str) -> str:
        result = mcp_tools.write_file(path=path, content=content)
        return json.dumps(result)

    @server.tool(
        name="list_directory",
        title="List Directory",
        description="List directory contents with filtering, pagination, and file metadata",
    )
    def list_directory(path: str = ".", pattern: str = "*", recursive: bool = False) -> str:
        result = mcp_tools.list_directory(path=path, pattern=pattern, recursive=recursive)
        return json.dumps(result)


def create_code_tools(server: MCPServer) -> None:
    """Register code analysis tools (delegating to tools.py)."""

    @server.tool(
        name="search_code",
        title="Search Code",
        description="Search for regex patterns in code files with file type filtering and match statistics",
    )
    def search_code(
        pattern: str,
        path: str = ".",
        file_types: str = ".py,.js,.ts",
        max_results: int = 50,
    ) -> str:
        type_list = [e.strip() for e in file_types.split(",")]
        result = mcp_tools.search_codebase(
            pattern=pattern,
            path=path,
            file_types=type_list,
            max_results=max_results,
        )
        return json.dumps(result)

    @server.tool(
        name="analyze_python_file",
        title="Analyze Python File",
        description="Analyze a Python file's structure: classes, functions, imports, metrics, and base classes",
    )
    def analyze_python_file(path: str) -> str:
        result = mcp_tools.analyze_python_file(path=path)
        return json.dumps(result)


def create_shell_tools(server: MCPServer) -> None:
    """Register shell command tools (delegating to tools.py)."""

    @server.tool(
        name="run_command",
        title="Run Command",
        description="Execute a shell command with environment variable support and structured output",
    )
    def run_command(command: str, cwd: str = ".", timeout: int = 30) -> str:
        result = mcp_tools.run_shell_command(command=command, cwd=cwd, timeout=timeout)
        return json.dumps(result)


def create_git_tools(server: MCPServer) -> None:
    """Register git operation tools (delegating to tools.py)."""

    @server.tool(
        name="git_status",
        title="Git Status",
        description="Get git repository status including branch, changed files, and recent commits",
    )
    def git_status(path: str = ".") -> str:
        result = mcp_tools.git_status(path=path)
        return json.dumps(result)

    @server.tool(
        name="git_diff",
        title="Git Diff",
        description="Get git diff showing file changes, optionally staged only",
    )
    def git_diff(path: str = ".", staged: bool = False) -> str:
        result = mcp_tools.git_diff(path=path, staged=staged)
        return json.dumps(result)


def create_data_tools(server: MCPServer) -> None:
    """Register data utility tools (delegating to tools.py)."""

    @server.tool(
        name="json_query",
        title="JSON Query",
        description="Read and query JSON files using dot-notation paths (e.g. 'data.items[0].name')",
    )
    def json_query(path: str, query: str = "") -> str:
        result = mcp_tools.json_query(path=path, query=query or None)
        return json.dumps(result)

    @server.tool(
        name="checksum_file",
        title="Checksum File",
        description="Calculate file checksum using md5, sha1, or sha256 algorithms",
    )
    def checksum_file(path: str, algorithm: str = "sha256") -> str:
        result = mcp_tools.checksum_file(path=path, algorithm=algorithm)
        return json.dumps(result)


def create_memory_tools(server: MCPServer) -> None:
    """Register memory/context tools."""

    _memory_store: Dict[str, str] = {}

    @server.tool(name="store_memory", title="Store Memory", description="Store a key-value pair in temporary memory")
    def store_memory(key: str, value: str) -> str:
        _memory_store[key] = value
        return f"Stored '{key}' in memory"

    @server.tool(name="recall_memory", title="Recall Memory", description="Retrieve a value from temporary memory")
    def recall_memory(key: str) -> str:
        if key in _memory_store:
            return _memory_store[key]
        return f"Key '{key}' not found in memory"

    @server.tool(name="list_memories", title="List Memories", description="List all keys stored in temporary memory")
    def list_memories() -> str:
        if _memory_store:
            return "\n".join(f"- {k}" for k in _memory_store.keys())
        return "Memory is empty"


def create_codomyrmex_tools(server: MCPServer) -> None:
    """Register Codomyrmex-specific tools."""

    @server.tool(name="list_modules", title="List Modules", description="List all available Codomyrmex modules")
    def list_modules() -> str:
        try:
            from codomyrmex import list_modules as lm
            modules = lm()
            return "\n".join(f"- {m}" for m in sorted(modules))
        except Exception as e:
            return f"Error: {e}"

    @server.tool(name="get_module_info", title="Module Info", description="Get information about a Codomyrmex module")
    def get_module_info(module_name: str) -> str:
        try:
            module_path = Path(__file__).parent.parent.parent / "src" / "codomyrmex" / module_name

            info = [f"Module: {module_name}"]

            # Check for README
            readme = module_path / "README.md"
            if readme.exists():
                content = readme.read_text()
                info.append(f"\nDescription:\n{content[:500]}...")

            # List files
            if module_path.exists():
                files = [f.name for f in module_path.iterdir() if f.is_file()]
                info.append(f"\nFiles: {', '.join(files[:10])}")

            return "\n".join(info)
        except Exception as e:
            return f"Error: {e}"


# ============================================================================
# Server Management
# ============================================================================

def create_server(name: str = "codomyrmex-mcp") -> MCPServer:
    """Create and configure an MCP server with all tools."""
    config = MCPServerConfig(name=name, version="1.0.0")
    server = MCPServer(config)

    # Register all built-in tool categories (delegating to tools.py)
    create_file_tools(server)
    create_code_tools(server)
    create_shell_tools(server)
    create_git_tools(server)
    create_data_tools(server)
    create_memory_tools(server)
    create_codomyrmex_tools(server)

    # Discover and register tools from MCP_TOOL_SPECIFICATION.md files
    try:
        discovered_count = discover_and_register_tools(server)
        logger.info(f"Discovery bridge registered {discovered_count} additional tools")
    except Exception as e:
        logger.warning(f"Tool discovery failed (non-fatal): {e}")

    # Register resources
    project_root = Path(__file__).parent.parent.parent
    server.register_resource(
        uri=f"file://{project_root}/README.md",
        name="Codomyrmex README",
        description="Main project documentation",
        mime_type="text/markdown",
    )

    # Register prompts
    server.register_prompt(
        name="code_review",
        description="Prompt for reviewing code changes",
        template="Please review the following code for: {focus}\n\nCode:\n{code}",
        arguments=[
            {"name": "focus", "description": "What to focus on (security, performance, style)"},
            {"name": "code", "description": "The code to review"},
        ]
    )

    server.register_prompt(
        name="explain_code",
        description="Prompt for explaining code",
        template="Explain this code in {detail_level} detail:\n\n{code}",
        arguments=[
            {"name": "detail_level", "description": "Level of detail (brief, detailed, expert)"},
            {"name": "code", "description": "The code to explain"},
        ]
    )

    return server


def list_available_tools(server: MCPServer) -> None:
    """Print all available tools."""
    tools = server._tool_registry.list_tools()

    print("Available MCP Tools\n")
    print(f"Total: {len(tools)} tools\n")

    for name in sorted(tools):
        tool = server._tool_registry.get(name)
        if tool:
            schema = tool.get("schema", {})
            desc = schema.get("description", "No description")
            status = schema.get("_implementation_status", "fully_implemented")
            status_label = "[IMPL]" if status == "fully_implemented" else "[SPEC]"

            print(f"  {status_label} {name}")
            print(f"     {desc}")

            input_schema = schema.get("inputSchema", {})
            params = input_schema.get("properties", {})
            if params:
                print(f"     Parameters: {', '.join(params.keys())}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="Run Codomyrmex MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_mcp_server.py                    # Run stdio server
  python run_mcp_server.py --list-tools       # List available tools
  python run_mcp_server.py --transport http   # Run HTTP server (browser access)
        """
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP transport (default: 8080)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for HTTP transport (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available tools and exit"
    )
    parser.add_argument(
        "--name",
        default="codomyrmex-mcp",
        help="Server name (default: codomyrmex-mcp)"
    )

    args = parser.parse_args()

    # Create server
    server = create_server(name=args.name)

    if args.list_tools:
        list_available_tools(server)
        return 0

    # Run server
    if args.transport == "stdio":
        print("Starting Codomyrmex MCP Server (stdio)", file=sys.stderr)
        print(f"   Tools: {len(server._tool_registry.list_tools())}", file=sys.stderr)
        print("   Press Ctrl+C to stop\n", file=sys.stderr)
        server.run()
    else:
        tool_count = len(server._tool_registry.list_tools())
        print(f"Starting Codomyrmex MCP Server (HTTP)", file=sys.stderr)
        print(f"   URL: http://{args.host}:{args.port}", file=sys.stderr)
        print(f"   Tools: {tool_count}", file=sys.stderr)
        print(f"   Web UI: http://localhost:{args.port}/", file=sys.stderr)
        print(f"   Health: http://localhost:{args.port}/health", file=sys.stderr)
        print("   Press Ctrl+C to stop\n", file=sys.stderr)
        asyncio.run(server.run_http(host=args.host, port=args.port))

    return 0


if __name__ == "__main__":
    sys.exit(main())
