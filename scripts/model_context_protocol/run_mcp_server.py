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
import contextlib
import json
import os

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol import MCPServer, MCPServerConfig
from codomyrmex.model_context_protocol import tools as mcp_tools
from codomyrmex.model_context_protocol.discovery import MCPDiscovery

logger = get_logger(__name__)

READONLY_TOOL_NAMES = frozenset(
    {
        "git_diff",
        "git_status",
        "read_file",
        "list_directory",
        "search_code",
        "analyze_python_file",
        "json_query",
        "checksum_file",
        "list_modules",
        "get_module_info",
    }
)


# ============================================================================
# MCP Tool Discovery Bridge
# ============================================================================


def discover_and_register_tools(server: MCPServer) -> int:
    """Discover decorated executable tools and register them with the server."""
    discovery = MCPDiscovery()
    # MCP stdio reserves stdout for JSON-RPC frames. Some optional modules emit
    # import-time diagnostics, so keep discovery noise on stderr.
    with contextlib.redirect_stdout(sys.stderr):
        report = discovery.scan_package("codomyrmex")
    registered_count = 0
    existing = set(server._tool_registry.list_tools())

    for tool in report.tools:
        if not tool.available or tool.handler is None:
            continue

        tool_name = tool.name.strip()
        if not tool_name or tool_name in existing:
            continue

        schema = {
            "name": tool_name,
            "description": tool.description or f"Discovered tool: {tool_name}",
            "inputSchema": tool.parameters
            or {
                "type": "object",
                "properties": {},
                "required": [],
            },
            "x-codomyrmex": {
                "module": tool.module_path,
                "callable": tool.callable_name,
                "version": tool.version,
                "tags": tool.tags,
            },
        }

        server.register_tool(tool_name, schema, tool.handler)
        existing.add(tool_name)

        registered_count += 1
        logger.debug("Registered discovered tool: %s", tool_name)

    if report.failed_modules:
        logger.warning("Tool discovery skipped %d modules", len(report.failed_modules))
    logger.info("Registered %d discovered executable tools", registered_count)
    return registered_count


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
    def list_directory(
        path: str = ".", pattern: str = "*", recursive: bool = False
    ) -> str:
        result = mcp_tools.list_directory(
            path=path, pattern=pattern, recursive=recursive
        )
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

    _memory_store: dict[str, str] = {}

    @server.tool(
        name="store_memory",
        title="Store Memory",
        description="Store a key-value pair in temporary memory",
    )
    def store_memory(key: str, value: str) -> str:
        _memory_store[key] = value
        return f"Stored '{key}' in memory"

    @server.tool(
        name="recall_memory",
        title="Recall Memory",
        description="Retrieve a value from temporary memory",
    )
    def recall_memory(key: str) -> str:
        if key in _memory_store:
            return _memory_store[key]
        return f"Key '{key}' not found in memory"

    @server.tool(
        name="list_memories",
        title="List Memories",
        description="List all keys stored in temporary memory",
    )
    def list_memories() -> str:
        if _memory_store:
            return "\n".join(f"- {k}" for k in _memory_store)
        return "Memory is empty"


def create_codomyrmex_tools(server: MCPServer) -> None:
    """Register Codomyrmex-specific tools."""

    @server.tool(
        name="list_modules",
        title="List Modules",
        description="List all available Codomyrmex modules",
    )
    def list_modules() -> str:
        try:
            from codomyrmex import list_modules as lm

            modules = lm()
            return "\n".join(f"- {m}" for m in sorted(modules))
        except Exception as e:
            return f"Error: {e}"

    @server.tool(
        name="get_module_info",
        title="Module Info",
        description="Get information about a Codomyrmex module",
    )
    def get_module_info(module_name: str) -> str:
        try:
            module_path = (
                Path(__file__).parent.parent.parent / "src" / "codomyrmex" / module_name
            )

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
            {
                "name": "focus",
                "description": "What to focus on (security, performance, style)",
            },
            {"name": "code", "description": "The code to review"},
        ],
    )

    server.register_prompt(
        name="explain_code",
        description="Prompt for explaining code",
        template="Explain this code in {detail_level} detail:\n\n{code}",
        arguments=[
            {
                "name": "detail_level",
                "description": "Level of detail (brief, detailed, expert)",
            },
            {"name": "code", "description": "The code to explain"},
        ],
    )

    return server


def apply_tool_profile(server: MCPServer, profile: str) -> None:
    """Restrict the server registry to a named tool profile."""
    if profile == "full":
        return
    if profile != "readonly":
        raise ValueError(f"Unknown tool profile: {profile}")

    for tool_name in list(server._tool_registry.list_tools()):
        if tool_name not in READONLY_TOOL_NAMES:
            server._tool_registry.unregister(tool_name)
    logger.info(
        "Applied readonly MCP tool profile with %d tools",
        len(server._tool_registry.list_tools()),
    )


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


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser without starting discovery or a server."""
    parser = argparse.ArgumentParser(
        description="Run Codomyrmex MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_mcp_server.py                    # Run stdio server
  python run_mcp_server.py --list-tools       # List available tools
  python run_mcp_server.py --transport http   # Run HTTP server (browser access)
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP transport (default: 8080)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--list-tools", action="store_true", help="List available tools and exit"
    )
    parser.add_argument(
        "--name", default="codomyrmex-mcp", help="Server name (default: codomyrmex-mcp)"
    )
    parser.add_argument(
        "--profile",
        choices=["full", "readonly"],
        default=None,
        help="Tool exposure profile (HTTP defaults to readonly; stdio defaults to full)",
    )
    parser.add_argument(
        "--auth-token",
        default=None,
        help="Bearer token for HTTP; may also be set via CODOMYRMEX_MCP_AUTH_TOKEN",
    )
    parser.add_argument(
        "--cors-origin",
        action="append",
        default=[],
        help="Explicit browser origin allowed by HTTP CORS (repeatable)",
    )
    return parser


def resolve_profile(transport: str, profile: str | None) -> str:
    """Resolve the safe default tool profile for a selected transport."""
    return profile or ("readonly" if transport == "http" else "full")


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "model_context_protocol"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print(
                "Loaded config from config/model_context_protocol/config.yaml",
                file=sys.stderr,
            )

    parser = build_parser()
    args = parser.parse_args()

    profile = resolve_profile(args.transport, args.profile)

    # Create server
    server = create_server(name=args.name)
    apply_tool_profile(server, profile)

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
        print("Starting Codomyrmex MCP Server (HTTP)", file=sys.stderr)
        print(f"   URL: http://{args.host}:{args.port}", file=sys.stderr)
        print(f"   Tools: {tool_count}", file=sys.stderr)
        print(f"   Web UI: http://localhost:{args.port}/", file=sys.stderr)
        print(f"   Health: http://localhost:{args.port}/health", file=sys.stderr)
        print("   Press Ctrl+C to stop\n", file=sys.stderr)
        asyncio.run(
            server.run_http(
                host=args.host,
                port=args.port,
                allowed_origins=args.cors_origin,
                auth_token=args.auth_token
                or os.environ.get("CODOMYRMEX_MCP_AUTH_TOKEN"),
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
