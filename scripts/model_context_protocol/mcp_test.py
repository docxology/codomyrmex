#!/usr/bin/env python3
"""
MCP Test Runner

Runs tests against MCP servers and tools.

Usage:
    python mcp_test.py                    # Run all tests
    python mcp_test.py --smoke            # Run smoke tests only
    python mcp_test.py --tool read_file   # Test specific tool
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import asyncio

from codomyrmex.model_context_protocol import MCPServer
from codomyrmex.model_context_protocol.testing import (
    ServerTester,
    MockMCPClient,
)
from codomyrmex.model_context_protocol.validators import (
    MessageValidator,
)


def create_test_server():
    """Create a test server with sample tools."""
    server = MCPServer()
    
    @server.tool(name="echo", description="Echo back the input")
    def echo(message: str) -> str:
        return message
    
    @server.tool(name="add", description="Add two numbers")
    def add(a: int, b: int) -> int:
        return a + b
    
    @server.tool(name="greet", description="Generate a greeting")
    def greet(name: str, formal: bool = False) -> str:
        if formal:
            return f"Good day, {name}."
        return f"Hello, {name}!"
    
    return server


async def run_smoke_tests(server) -> None:
    """Run smoke tests."""
    print("🧪 Running Smoke Tests\n")
    
    tester = ServerTester(server)
    suite = await tester.run_smoke_tests()
    
    for result in suite.results:
        status = "✓" if result.passed else "✗"
        print(f"  {status} {result.name} ({result.duration_ms:.1f}ms)")
        if not result.passed and result.error:
            print(f"      Error: {result.error}")
    
    print(f"\n{suite.summary()}")


async def run_tool_tests(server, tool_name: str) -> None:
    """Run tests for a specific tool."""
    print(f"🔧 Testing Tool: {tool_name}\n")
    
    client = MockMCPClient(server)
    
    # Initialize first
    await client.initialize()
    
    # Get tool list
    tools_response = await client.list_tools()
    if "result" not in tools_response:
        print("❌ Failed to get tools list")
        return
    
    tools = tools_response["result"].get("tools", [])
    tool_names = [t.get("name") for t in tools]
    
    if tool_name not in tool_names:
        print(f"❌ Tool '{tool_name}' not found")
        print(f"   Available: {', '.join(tool_names)}")
        return
    
    # Test the tool with sample arguments
    print(f"  Calling {tool_name}...")
    
    # Build simple test arguments based on tool name
    test_args = {}
    if tool_name == "echo":
        test_args = {"message": "Hello, MCP!"}
    elif tool_name == "add":
        test_args = {"a": 5, "b": 3}
    elif tool_name == "greet":
        test_args = {"name": "World"}
    
    response = await client.call_tool(tool_name, test_args)
    
    if "result" in response:
        print(f"  ✓ Call succeeded")
        content = response["result"].get("content", [])
        if content:
            print(f"    Output: {content[0].get('text', '')[:100]}")
    else:
        print(f"  ✗ Call failed")
        if "error" in response:
            print(f"    Error: {response['error'].get('message')}")


async def run_validation_tests() -> None:
    """Run message validation tests."""
    print("📋 Running Validation Tests\n")
    
    validator = MessageValidator()
    
    test_cases = [
        {
            "name": "Valid request",
            "message": {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            "type": "request",
            "should_pass": True,
        },
        {
            "name": "Missing method",
            "message": {"jsonrpc": "2.0", "id": 1},
            "type": "request",
            "should_pass": False,
        },
        {
            "name": "Valid response",
            "message": {"jsonrpc": "2.0", "id": 1, "result": {"tools": []}},
            "type": "response",
            "should_pass": True,
        },
        {
            "name": "Response with both result and error",
            "message": {"jsonrpc": "2.0", "id": 1, "result": {}, "error": {}},
            "type": "response",
            "should_pass": False,
        },
    ]
    
    passed = 0
    for case in test_cases:
        if case["type"] == "request":
            result = validator.validate_request(case["message"])
        else:
            result = validator.validate_response(case["message"])
        
        actual_pass = result.valid
        expected_pass = case["should_pass"]
        
        if actual_pass == expected_pass:
            print(f"  ✓ {case['name']}")
            passed += 1
        else:
            print(f"  ✗ {case['name']} (expected {'pass' if expected_pass else 'fail'})")
            if result.errors:
                print(f"    Errors: {result.errors}")
    
    print(f"\n{passed}/{len(test_cases)} validation tests passed")


async def run_all_tests() -> None:
    """Run all test suites."""
    server = create_test_server()
    
    await run_smoke_tests(server)
    print()
    await run_validation_tests()


def main():
    parser = argparse.ArgumentParser(
        description="MCP Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    parser.add_argument("--tool", "-t", help="Test specific tool")
    parser.add_argument("--validation", action="store_true", help="Run validation tests")
    
    args = parser.parse_args()
    
    server = create_test_server()
    
    if args.smoke:
        asyncio.run(run_smoke_tests(server))
    elif args.tool:
        asyncio.run(run_tool_tests(server, args.tool))
    elif args.validation:
        asyncio.run(run_validation_tests())
    else:
        asyncio.run(run_all_tests())
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
