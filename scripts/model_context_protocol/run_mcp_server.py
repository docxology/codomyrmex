#!/usr/bin/env python3
"""
MCP Server Runner - Start an MCP server with Codomyrmex tools.

Usage:
    python run_mcp_server.py [--transport stdio|http] [--port 8080]

Examples:
    # Run stdio server for Claude Desktop
    python run_mcp_server.py --transport stdio
    
    # Run HTTP server for remote access
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
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


# ============================================================================
# Built-in Codomyrmex Tools
# ============================================================================

def create_file_tools(server: MCPServer) -> None:
    """Register file operation tools."""
    
    @server.tool(name="read_file", description="Read the contents of a file at the specified path")
    def read_file(path: str, encoding: str = "utf-8") -> str:
        """Read file contents."""
        try:
            return Path(path).read_text(encoding=encoding)
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except Exception as e:
            return f"Error: {e}"
    
    @server.tool(name="write_file", description="Write content to a file, creating it if it doesn't exist")
    def write_file(path: str, content: str) -> str:
        """Write content to file."""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content)
            return f"Successfully wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error: {e}"
    
    @server.tool(name="list_directory", description="List files and directories in a path")
    def list_directory(path: str = ".", recursive: bool = False) -> str:
        """List directory contents."""
        try:
            p = Path(path)
            if recursive:
                items = list(p.rglob("*"))[:100]  # Limit for safety
            else:
                items = list(p.iterdir())
            
            result = []
            for item in sorted(items):
                prefix = "📁" if item.is_dir() else "📄"
                result.append(f"{prefix} {item.name}")
            
            return "\n".join(result) if result else "Empty directory"
        except Exception as e:
            return f"Error: {e}"


def create_code_tools(server: MCPServer) -> None:
    """Register code analysis tools."""
    
    @server.tool(name="search_code", description="Search for patterns in code files using grep-like search")
    def search_code(
        pattern: str,
        path: str = ".",
        file_types: str = ".py,.js,.ts",
        max_results: int = 50,
    ) -> str:
        """Search for pattern in files."""
        import re
        
        results = []
        extensions = [e.strip() for e in file_types.split(",")]
        
        try:
            for filepath in Path(path).rglob("*"):
                if not filepath.is_file():
                    continue
                if not any(filepath.suffix == ext for ext in extensions):
                    continue
                
                try:
                    content = filepath.read_text(errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            results.append(f"{filepath}:{i}: {line.strip()[:100]}")
                            if len(results) >= max_results:
                                break
                except Exception:
                    continue
                
                if len(results) >= max_results:
                    break
            
            if results:
                return f"Found {len(results)} matches:\n" + "\n".join(results)
            return f"No matches found for pattern: {pattern}"
        except Exception as e:
            return f"Error: {e}"
    
    @server.tool(name="get_file_outline", description="Get the structure/outline of a Python file (classes, functions)")
    def get_file_outline(path: str) -> str:
        """Get file structure."""
        import ast
        
        try:
            content = Path(path).read_text()
            tree = ast.parse(content)
            
            outline = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    outline.append(f"class {node.name} (line {node.lineno})")
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            outline.append(f"    def {item.name}() (line {item.lineno})")
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    outline.append(f"def {node.name}() (line {node.lineno})")
            
            return "\n".join(outline) if outline else "No classes or functions found"
        except Exception as e:
            return f"Error: {e}"


def create_shell_tools(server: MCPServer) -> None:
    """Register shell command tools."""
    
    @server.tool(name="run_command", description="Execute a shell command and return its output")
    def run_command(command: str, cwd: str = ".", timeout: int = 30) -> str:
        """Run a shell command."""
        import subprocess
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"Exit code: {result.returncode}"
            
            return output
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Error: {e}"


def create_memory_tools(server: MCPServer) -> None:
    """Register memory/context tools."""
    
    _memory_store: Dict[str, str] = {}
    
    @server.tool(name="store_memory", description="Store a key-value pair in temporary memory")
    def store_memory(key: str, value: str) -> str:
        """Store a value in memory."""
        _memory_store[key] = value
        return f"Stored '{key}' in memory"
    
    @server.tool(name="recall_memory", description="Retrieve a value from temporary memory")
    def recall_memory(key: str) -> str:
        """Recall a value from memory."""
        if key in _memory_store:
            return _memory_store[key]
        return f"Key '{key}' not found in memory"
    
    @server.tool(name="list_memories", description="List all keys stored in temporary memory")
    def list_memories() -> str:
        """List all memory keys."""
        if _memory_store:
            return "\n".join(f"- {k}" for k in _memory_store.keys())
        return "Memory is empty"


def create_codomyrmex_tools(server: MCPServer) -> None:
    """Register Codomyrmex-specific tools."""
    
    @server.tool(name="list_modules", description="List all available Codomyrmex modules")
    def list_modules() -> str:
        """List Codomyrmex modules."""
        try:
            from codomyrmex import list_modules as lm
            modules = lm()
            return "\n".join(f"- {m}" for m in sorted(modules))
        except Exception as e:
            return f"Error: {e}"
    
    @server.tool(name="get_module_info", description="Get information about a Codomyrmex module")
    def get_module_info(module_name: str) -> str:
        """Get module info."""
        try:
            module_path = Path(__file__).parent.parent.parent / "src" / "codomyrmex" / module_name
            
            info = [f"Module: {module_name}"]
            
            # Check for README
            readme = module_path / "README.md"
            if readme.exists():
                content = readme.read_text()
                # Get first 500 chars
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
    
    # Register all tool categories
    create_file_tools(server)
    create_code_tools(server)
    create_shell_tools(server)
    create_memory_tools(server)
    create_codomyrmex_tools(server)
    
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
    
    print("🔧 Available MCP Tools\n")
    print(f"Total: {len(tools)} tools\n")
    
    for name in sorted(tools):
        tool = server._tool_registry.get(name)
        if tool:
            schema = tool.get("schema", {})
            desc = schema.get("description", "No description")
            print(f"  📌 {name}")
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
  python run_mcp_server.py --transport http   # Run HTTP server
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
        print("🚀 Starting Codomyrmex MCP Server (stdio)", file=sys.stderr)
        print(f"   Tools: {len(server._tool_registry.list_tools())}", file=sys.stderr)
        print("   Press Ctrl+C to stop\n", file=sys.stderr)
        server.run()
    else:
        print(f"HTTP transport not yet implemented", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
