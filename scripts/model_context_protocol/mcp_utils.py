#!/usr/bin/env python3
"""
MCP (Model Context Protocol) server utilities.

Usage:
    python mcp_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json


# Example MCP tool definitions
MCP_TOOLS = {
    "execute_code": {
        "description": "Execute code in a sandbox environment",
        "parameters": {
            "language": {"type": "string", "required": True},
            "code": {"type": "string", "required": True},
            "timeout": {"type": "integer", "default": 30},
        },
    },
    "read_file": {
        "description": "Read contents of a file",
        "parameters": {
            "path": {"type": "string", "required": True},
            "encoding": {"type": "string", "default": "utf-8"},
        },
    },
    "write_file": {
        "description": "Write content to a file",
        "parameters": {
            "path": {"type": "string", "required": True},
            "content": {"type": "string", "required": True},
        },
    },
    "search_files": {
        "description": "Search for patterns in files",
        "parameters": {
            "pattern": {"type": "string", "required": True},
            "path": {"type": "string", "default": "."},
            "file_types": {"type": "array", "default": [".py"]},
        },
    },
}


def list_tools() -> list:
    """List available MCP tools."""
    return [{"name": k, **v} for k, v in MCP_TOOLS.items()]


def validate_tool_call(tool_name: str, args: dict) -> tuple:
    """Validate a tool call."""
    if tool_name not in MCP_TOOLS:
        return False, f"Unknown tool: {tool_name}"
    
    tool = MCP_TOOLS[tool_name]
    errors = []
    
    for param, spec in tool["parameters"].items():
        if spec.get("required") and param not in args:
            errors.append(f"Missing required parameter: {param}")
    
    return (len(errors) == 0), errors


def generate_tool_schema(tool_name: str) -> dict:
    """Generate JSON Schema for a tool."""
    if tool_name not in MCP_TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}
    
    tool = MCP_TOOLS[tool_name]
    properties = {}
    required = []
    
    for param, spec in tool["parameters"].items():
        properties[param] = {"type": spec.get("type", "string")}
        if spec.get("default") is not None:
            properties[param]["default"] = spec["default"]
        if spec.get("required"):
            required.append(param)
    
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def main():
    parser = argparse.ArgumentParser(description="MCP utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # List command
    subparsers.add_parser("list", help="List available tools")
    
    # Schema command
    schema = subparsers.add_parser("schema", help="Get tool schema")
    schema.add_argument("tool", help="Tool name")
    
    # Validate command
    validate = subparsers.add_parser("validate", help="Validate tool call")
    validate.add_argument("tool", help="Tool name")
    validate.add_argument("--args", "-a", default="{}", help="Arguments as JSON")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🔧 MCP Utilities\n")
        print("Commands:")
        print("  list     - List available MCP tools")
        print("  schema   - Get JSON Schema for a tool")
        print("  validate - Validate a tool call")
        print("\nExamples:")
        print("  python mcp_utils.py list")
        print("  python mcp_utils.py schema execute_code")
        print('  python mcp_utils.py validate execute_code --args \'{"language":"python","code":"print(1)"}\'')
        return 0
    
    if args.command == "list":
        tools = list_tools()
        print(f"📋 Available MCP Tools ({len(tools)}):\n")
        for tool in tools:
            print(f"   🔧 {tool['name']}")
            print(f"      {tool['description']}")
            params = list(tool['parameters'].keys())
            print(f"      Parameters: {', '.join(params)}")
            print()
    
    elif args.command == "schema":
        schema = generate_tool_schema(args.tool)
        print(f"📄 Schema for '{args.tool}':\n")
        print(json.dumps(schema, indent=2))
    
    elif args.command == "validate":
        try:
            call_args = json.loads(args.args)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON: {args.args}")
            return 1
        
        valid, errors = validate_tool_call(args.tool, call_args)
        
        if valid:
            print(f"✅ Valid tool call: {args.tool}")
            print(f"   Arguments: {call_args}")
        else:
            print(f"❌ Invalid tool call: {args.tool}")
            for e in errors:
                print(f"   • {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
