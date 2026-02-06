#!/usr/bin/env python3
"""
Comprehensive MCP Test Suite

Tests all MCP components: servers, tools, discovery, validation, and integration.

Usage:
    python mcp_comprehensive_test.py                 # Run all tests
    python mcp_comprehensive_test.py --category tools  # Run tool tests only
    python mcp_comprehensive_test.py --verbose        # Verbose output
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
import tempfile
import time
from typing import Dict, List, Any


# ============================================================================
# TEST INFRASTRUCTURE
# ============================================================================

class TestRunner:
    """Test runner with detailed reporting."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: Dict[str, List[Dict]] = {}
        self.start_time = None
    
    def run_test(self, category: str, name: str, test_func):
        """Run a single test."""
        if category not in self.results:
            self.results[category] = []
        
        start = time.perf_counter()
        try:
            result = test_func()
            duration = (time.perf_counter() - start) * 1000
            
            passed = result if isinstance(result, bool) else bool(result)
            
            self.results[category].append({
                "name": name,
                "passed": passed,
                "duration_ms": round(duration, 2),
                "error": None,
            })
            
            if self.verbose:
                status = "✓" if passed else "✗"
                print(f"  {status} {name} ({duration:.1f}ms)")
            
            return passed
            
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            
            self.results[category].append({
                "name": name,
                "passed": False,
                "duration_ms": round(duration, 2),
                "error": str(e),
            })
            
            if self.verbose:
                print(f"  ✗ {name} - {e}")
            
            return False
    
    def summary(self) -> Dict[str, Any]:
        """Generate test summary."""
        total = sum(len(tests) for tests in self.results.values())
        passed = sum(
            sum(1 for t in tests if t["passed"])
            for tests in self.results.values()
        )
        
        by_category = {}
        for cat, tests in self.results.items():
            cat_passed = sum(1 for t in tests if t["passed"])
            by_category[cat] = {
                "passed": cat_passed,
                "failed": len(tests) - cat_passed,
                "total": len(tests),
            }
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": passed / total if total > 0 else 0,
            "by_category": by_category,
        }
    
    def print_report(self):
        """Print detailed test report."""
        summary = self.summary()
        
        print("\n" + "=" * 60)
        print("MCP TEST SUITE RESULTS")
        print("=" * 60)
        
        for category, stats in summary["by_category"].items():
            status = "✓" if stats["failed"] == 0 else "✗"
            print(f"\n{status} {category}: {stats['passed']}/{stats['total']} passed")
            
            # Show failures
            for test in self.results.get(category, []):
                if not test["passed"]:
                    print(f"    ✗ {test['name']}")
                    if test["error"]:
                        print(f"      Error: {test['error']}")
        
        print("\n" + "-" * 60)
        rate = summary["success_rate"] * 100
        status = "PASSED" if summary["failed"] == 0 else "FAILED"
        print(f"Total: {summary['passed']}/{summary['total']} ({rate:.1f}%) - {status}")
        print("=" * 60)


# ============================================================================
# TOOL TESTS
# ============================================================================

def run_tool_tests(runner: TestRunner):
    """Test functional MCP tools."""
    from codomyrmex.model_context_protocol.tools import (
        read_file, write_file, list_directory,
        analyze_python_file, search_codebase,
        run_shell_command, json_query, checksum_file,
    )
    
    print("\n📦 Testing MCP Tools...")
    
    # read_file tests
    runner.run_test("tools", "read_file - valid file", lambda: (
        read_file(__file__)["success"]
    ))
    
    runner.run_test("tools", "read_file - nonexistent", lambda: (
        not read_file("/nonexistent/file.txt")["success"]
    ))
    
    # write_file tests
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        temp_path = f.name
    
    runner.run_test("tools", "write_file - create file", lambda: (
        write_file(temp_path, "Hello, MCP!")["success"]
    ))
    
    runner.run_test("tools", "write_file - verify content", lambda: (
        read_file(temp_path)["content"] == "Hello, MCP!"
    ))
    
    # list_directory tests
    runner.run_test("tools", "list_directory - current dir", lambda: (
        list_directory(".")["success"]
    ))
    
    runner.run_test("tools", "list_directory - with pattern", lambda: (
        len(list_directory(".", pattern="*.py")["items"]) > 0
    ))
    
    # analyze_python_file tests
    runner.run_test("tools", "analyze_python_file - this file", lambda: (
        analyze_python_file(__file__)["success"]
    ))
    
    runner.run_test("tools", "analyze_python_file - has functions", lambda: (
        len(analyze_python_file(__file__)["functions"]) > 0
    ))
    
    # search_codebase tests
    runner.run_test("tools", "search_codebase - find pattern", lambda: (
        search_codebase("def ", ".", [".py"])["success"]
    ))
    
    # run_shell_command tests
    runner.run_test("tools", "run_shell_command - echo", lambda: (
        "hello" in run_shell_command("echo hello")["stdout"]
    ))
    
    runner.run_test("tools", "run_shell_command - pwd", lambda: (
        run_shell_command("pwd")["success"]
    ))
    
    # json_query tests
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump({"name": "test", "items": [1, 2, 3]}, f)
        json_path = f.name
    
    runner.run_test("tools", "json_query - read file", lambda: (
        json_query(json_path)["success"]
    ))
    
    runner.run_test("tools", "json_query - query path", lambda: (
        json_query(json_path, "name")["result"] == "test"
    ))
    
    # checksum_file tests
    runner.run_test("tools", "checksum_file - sha256", lambda: (
        len(checksum_file(__file__)["checksum"]) == 64
    ))
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)
    Path(json_path).unlink(missing_ok=True)


# ============================================================================
# SERVER TESTS
# ============================================================================

def run_server_tests(runner: TestRunner):
    """Test MCP server implementation."""
    from codomyrmex.model_context_protocol import MCPServer
    from codomyrmex.model_context_protocol.testing import MockMCPClient
    
    print("\n🖥️  Testing MCP Server...")
    
    # Create test server
    server = MCPServer()
    
    @server.tool(name="test_echo", description="Echo test")
    def test_echo(message: str) -> str:
        return f"Echo: {message}"
    
    @server.tool(name="test_add", description="Add test")
    def test_add(a: int, b: int) -> int:
        return a + b
    
    # Server registration tests
    runner.run_test("server", "tool registration", lambda: (
        len(server._tool_registry.list_tools()) >= 2
    ))
    
    # Async tests using run_until_complete
    async def test_initialize():
        client = MockMCPClient(server)
        response = await client.initialize()
        return "result" in response and "protocolVersion" in response["result"]
    
    runner.run_test("server", "initialize handshake", lambda: (
        asyncio.get_event_loop().run_until_complete(test_initialize())
    ))
    
    async def test_list_tools():
        client = MockMCPClient(server)
        await client.initialize()
        response = await client.list_tools()
        return "result" in response and "tools" in response["result"]
    
    runner.run_test("server", "tools/list endpoint", lambda: (
        asyncio.get_event_loop().run_until_complete(test_list_tools())
    ))
    
    async def test_tool_call():
        client = MockMCPClient(server)
        await client.initialize()
        response = await client.call_tool("test_echo", {"message": "hello"})
        return "result" in response
    
    runner.run_test("server", "tools/call endpoint", lambda: (
        asyncio.get_event_loop().run_until_complete(test_tool_call())
    ))
    
    # Resource tests
    server.register_resource(
        uri="test://resource",
        name="Test Resource",
        description="A test resource",
    )
    
    runner.run_test("server", "resource registration", lambda: (
        len(server._resources) > 0
    ))
    
    # Prompt tests
    server.register_prompt(
        name="test_prompt",
        description="A test prompt",
        template="Hello, {name}!",
    )
    
    runner.run_test("server", "prompt registration", lambda: (
        len(server._prompts) > 0
    ))


# ============================================================================
# VALIDATOR TESTS
# ============================================================================

def run_validator_tests(runner: TestRunner):
    """Test MCP validators."""
    from codomyrmex.model_context_protocol.validators import (
        SchemaValidator, MessageValidator, ToolCallValidator, ValidationResult
    )
    
    print("\n✅ Testing Validators...")
    
    # Schema validator tests
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"]
    }
    validator = SchemaValidator(schema)
    
    runner.run_test("validators", "schema - valid object", lambda: (
        validator.validate({"name": "test", "age": 25}).valid
    ))
    
    runner.run_test("validators", "schema - missing required", lambda: (
        not validator.validate({"age": 25}).valid
    ))
    
    runner.run_test("validators", "schema - wrong type", lambda: (
        not validator.validate({"name": 123}).valid
    ))
    
    # Message validator tests
    msg_validator = MessageValidator()
    
    runner.run_test("validators", "message - valid request", lambda: (
        msg_validator.validate_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test"
        }).valid
    ))
    
    runner.run_test("validators", "message - missing method", lambda: (
        not msg_validator.validate_request({
            "jsonrpc": "2.0",
            "id": 1
        }).valid
    ))
    
    runner.run_test("validators", "message - valid response", lambda: (
        msg_validator.validate_response({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {}
        }).valid
    ))
    
    runner.run_test("validators", "message - error response", lambda: (
        msg_validator.validate_response({
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -1, "message": "Error"}
        }).valid
    ))
    
    runner.run_test("validators", "message - both result and error", lambda: (
        not msg_validator.validate_response({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {},
            "error": {}
        }).valid
    ))
    
    # Tool call validator
    tool_schemas = {
        "echo": {
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"]
        }
    }
    tool_validator = ToolCallValidator(tool_schemas)
    
    runner.run_test("validators", "tool call - valid", lambda: (
        tool_validator.validate_call("echo", {"message": "hi"}).valid
    ))
    
    runner.run_test("validators", "tool call - unknown tool", lambda: (
        not tool_validator.validate_call("unknown", {}).valid
    ))


# ============================================================================
# DISCOVERY TESTS
# ============================================================================

def run_discovery_tests(runner: TestRunner):
    """Test MCP discovery."""
    from codomyrmex.model_context_protocol.discovery import (
        ModuleScanner, SpecificationScanner, ToolCatalog, DiscoveredTool
    )
    
    print("\n🔍 Testing Discovery...")
    
    # ToolCatalog tests
    catalog = ToolCatalog()
    
    tool = DiscoveredTool(
        name="test_tool",
        description="A test tool",
        source="test",
        source_path="/test/path",
        input_schema={"type": "object"},
        tags=["test", "example"],
    )
    
    catalog.add(tool)
    
    runner.run_test("discovery", "catalog - add tool", lambda: (
        catalog.get("test_tool") is not None
    ))
    
    runner.run_test("discovery", "catalog - list all", lambda: (
        len(catalog.list_all()) == 1
    ))
    
    runner.run_test("discovery", "catalog - search by name", lambda: (
        len(catalog.search(query="test")) == 1
    ))
    
    runner.run_test("discovery", "catalog - search by tag", lambda: (
        len(catalog.search(tags=["test"])) == 1
    ))
    
    runner.run_test("discovery", "catalog - to json", lambda: (
        "test_tool" in catalog.to_json()
    ))
    
    # SpecificationScanner tests
    spec_scanner = SpecificationScanner()
    project_root = Path(__file__).parent.parent.parent
    spec_path = project_root / "src" / "codomyrmex" / "llm" / "MCP_TOOL_SPECIFICATION.md"
    
    if spec_path.exists():
        runner.run_test("discovery", "spec scanner - parse file", lambda: (
            isinstance(spec_scanner.scan_spec_file(spec_path), list)
        ))


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def run_integration_tests(runner: TestRunner):
    """Test end-to-end MCP workflows."""
    from codomyrmex.model_context_protocol import MCPServer
    from codomyrmex.model_context_protocol.testing import MockMCPClient
    from codomyrmex.model_context_protocol.tools import read_file, checksum_file
    
    print("\n🔗 Testing Integration...")
    
    # Create server with real tools
    server = MCPServer()
    
    @server.tool(name="read_file", description="Read a file")
    def mcp_read_file(path: str) -> str:
        result = read_file(path)
        if result["success"]:
            return result["content"]
        return f"Error: {result['error']}"
    
    @server.tool(name="checksum", description="Get file checksum")
    def mcp_checksum(path: str) -> str:
        result = checksum_file(path)
        if result["success"]:
            return result["checksum"]
        return f"Error: {result['error']}"
    
    # Test real file operations through MCP
    async def test_read_integration():
        client = MockMCPClient(server)
        await client.initialize()
        response = await client.call_tool("read_file", {"path": __file__})
        return "result" in response
    
    runner.run_test("integration", "read file through MCP", lambda: (
        asyncio.get_event_loop().run_until_complete(test_read_integration())
    ))
    
    async def test_checksum_integration():
        client = MockMCPClient(server)
        await client.initialize()
        response = await client.call_tool("checksum", {"path": __file__})
        return "result" in response
    
    runner.run_test("integration", "checksum through MCP", lambda: (
        asyncio.get_event_loop().run_until_complete(test_checksum_integration())
    ))
    
    # Test workflow: read and process
    async def test_workflow():
        client = MockMCPClient(server)
        await client.initialize()
        
        # List tools
        tools_resp = await client.list_tools()
        tool_names = [t["name"] for t in tools_resp["result"]["tools"]]
        
        return "read_file" in tool_names and "checksum" in tool_names
    
    runner.run_test("integration", "multi-step workflow", lambda: (
        asyncio.get_event_loop().run_until_complete(test_workflow())
    ))


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="MCP Comprehensive Test Suite")
    parser.add_argument("--category", "-c", help="Run specific category")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MCP COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    runner = TestRunner(verbose=args.verbose)
    
    categories = {
        "tools": run_tool_tests,
        "server": run_server_tests,
        "validators": run_validator_tests,
        "discovery": run_discovery_tests,
        "integration": run_integration_tests,
    }
    
    if args.category:
        if args.category in categories:
            categories[args.category](runner)
        else:
            print(f"Unknown category: {args.category}")
            print(f"Available: {', '.join(categories.keys())}")
            return 1
    else:
        for category_func in categories.values():
            category_func(runner)
    
    runner.print_report()
    
    summary = runner.summary()
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
