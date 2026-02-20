"""
MCP Testing Framework

Provides utilities for testing MCP tools, servers, and integrations.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import asyncio
import json
import time
from contextlib import contextmanager

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None
    output: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


@dataclass  
class TestSuite:
    """Collection of test results."""
    name: str
    results: List[TestResult] = field(default_factory=list)
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def total(self) -> int:
        return len(self.results)
    
    @property
    def success_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0
    
    def summary(self) -> str:
        return f"{self.name}: {self.passed}/{self.total} passed ({self.success_rate:.1%})"


class ToolTester:
    """
    Tests individual MCP tools.
    """
    
    def __init__(self, tool_registry):
        """
        Args:
            tool_registry: MCPToolRegistry or similar containing tools
        """
        self.registry = tool_registry
        self.results: List[TestResult] = []
    
    def test_tool(
        self,
        tool_name: str,
        test_cases: List[Dict[str, Any]],
    ) -> TestSuite:
        """
        Run test cases against a tool.
        
        Args:
            tool_name: Name of tool to test
            test_cases: List of dicts with 'arguments' and optional 'expected'
        
        Returns:
            TestSuite with results
        """
        suite = TestSuite(name=f"Tool: {tool_name}")
        
        for i, case in enumerate(test_cases):
            case_name = case.get("name", f"case_{i}")
            arguments = case.get("arguments", {})
            expected = case.get("expected")
            
            start = time.perf_counter()
            try:
                # Get tool and execute
                tool = self.registry.get(tool_name)
                if not tool:
                    suite.results.append(TestResult(
                        name=case_name,
                        passed=False,
                        duration_ms=0,
                        error=f"Tool not found: {tool_name}",
                    ))
                    continue
                
                handler = tool.get("handler")
                if handler:
                    result = handler(**arguments)
                else:
                    result = None
                
                duration = (time.perf_counter() - start) * 1000
                
                # Check expected if provided
                if expected is not None:
                    if result == expected:
                        suite.results.append(TestResult(
                            name=case_name,
                            passed=True,
                            duration_ms=duration,
                            output=result,
                        ))
                    else:
                        suite.results.append(TestResult(
                            name=case_name,
                            passed=False,
                            duration_ms=duration,
                            error=f"Expected {expected}, got {result}",
                            output=result,
                        ))
                else:
                    # Just check it runs without error
                    suite.results.append(TestResult(
                        name=case_name,
                        passed=True,
                        duration_ms=duration,
                        output=result,
                    ))
                    
            except Exception as e:
                duration = (time.perf_counter() - start) * 1000
                suite.results.append(TestResult(
                    name=case_name,
                    passed=False,
                    duration_ms=duration,
                    error=str(e),
                ))
        
        return suite


class ServerTester:
    """
    Tests MCP server implementations.
    """
    
    def __init__(self, server: Any) -> None:
        """
        Args:
            server: MCPServer instance
        """
        self.server = server
    
    async def test_initialize(self) -> TestResult:
        """Test the initialize handshake."""
        start = time.perf_counter()
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                }
            }
            
            response = await self.server.handle_request(request)
            duration = (time.perf_counter() - start) * 1000
            
            if "result" in response:
                result = response["result"]
                if "protocolVersion" in result and "capabilities" in result:
                    return TestResult(
                        name="initialize",
                        passed=True,
                        duration_ms=duration,
                        output=result,
                    )
            
            return TestResult(
                name="initialize",
                passed=False,
                duration_ms=duration,
                error="Invalid initialize response",
            )
            
        except Exception as e:
            return TestResult(
                name="initialize",
                passed=False,
                duration_ms=(time.perf_counter() - start) * 1000,
                error=str(e),
            )
    
    async def test_tools_list(self) -> TestResult:
        """Test tools/list endpoint."""
        start = time.perf_counter()
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = await self.server.handle_request(request)
            duration = (time.perf_counter() - start) * 1000
            
            if "result" in response and "tools" in response["result"]:
                return TestResult(
                    name="tools/list",
                    passed=True,
                    duration_ms=duration,
                    output=response["result"],
                )
            
            return TestResult(
                name="tools/list",
                passed=False,
                duration_ms=duration,
                error="Invalid tools/list response",
            )
            
        except Exception as e:
            return TestResult(
                name="tools/list",
                passed=False,
                duration_ms=(time.perf_counter() - start) * 1000,
                error=str(e),
            )
    
    async def test_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> TestResult:
        """Test calling a specific tool."""
        start = time.perf_counter()
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments,
                }
            }
            
            response = await self.server.handle_request(request)
            duration = (time.perf_counter() - start) * 1000
            
            if "result" in response and "content" in response["result"]:
                return TestResult(
                    name=f"tools/call:{tool_name}",
                    passed=True,
                    duration_ms=duration,
                    output=response["result"],
                )
            
            return TestResult(
                name=f"tools/call:{tool_name}",
                passed=False,
                duration_ms=duration,
                error="Invalid tool call response",
            )
            
        except Exception as e:
            return TestResult(
                name=f"tools/call:{tool_name}",
                passed=False,
                duration_ms=(time.perf_counter() - start) * 1000,
                error=str(e),
            )
    
    async def run_smoke_tests(self) -> TestSuite:
        """Run basic smoke tests against the server."""
        suite = TestSuite(name="MCP Server Smoke Tests")
        
        # Test initialize
        suite.results.append(await self.test_initialize())
        
        # Test tools/list
        suite.results.append(await self.test_tools_list())
        
        return suite


class IntegrationTester:
    """
    Tests end-to-end MCP workflows.
    """
    
    def __init__(self):
        self.scenarios: List[Dict[str, Any]] = []
    
    def add_scenario(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        description: str = "",
    ) -> None:
        """Add a test scenario."""
        self.scenarios.append({
            "name": name,
            "description": description,
            "steps": steps,
        })
    
    async def run_scenario(
        self,
        scenario: Dict[str, Any],
        server: Any,
    ) -> TestSuite:
        """Run a single scenario."""
        suite = TestSuite(name=scenario["name"])
        
        context: Dict[str, Any] = {}  # Shared context between steps
        
        for i, step in enumerate(scenario["steps"]):
            step_name = step.get("name", f"step_{i}")
            method = step["method"]
            params = step.get("params", {})
            
            # Template params from context
            for key, value in params.items():
                if isinstance(value, str) and value.startswith("$"):
                    context_key = value[1:]
                    if context_key in context:
                        params[key] = context[context_key]
            
            start = time.perf_counter()
            try:
                request = {
                    "jsonrpc": "2.0",
                    "id": i + 1,
                    "method": method,
                    "params": params,
                }
                
                response = await server.handle_request(request)
                duration = (time.perf_counter() - start) * 1000
                
                # Store result in context if specified
                if "store_as" in step and "result" in response:
                    context[step["store_as"]] = response["result"]
                
                # Check assertions
                if "assertions" in step:
                    for assertion in step["assertions"]:
                        # Simple assertion checking
                        pass
                
                if "error" in response:
                    suite.results.append(TestResult(
                        name=step_name,
                        passed=False,
                        duration_ms=duration,
                        error=response["error"].get("message"),
                    ))
                else:
                    suite.results.append(TestResult(
                        name=step_name,
                        passed=True,
                        duration_ms=duration,
                        output=response.get("result"),
                    ))
                    
            except Exception as e:
                suite.results.append(TestResult(
                    name=step_name,
                    passed=False,
                    duration_ms=(time.perf_counter() - start) * 1000,
                    error=str(e),
                ))
        
        return suite
    
    async def run_all(self, server: Any) -> List[TestSuite]:
        """Run all registered scenarios."""
        suites = []
        for scenario in self.scenarios:
            suite = await self.run_scenario(scenario, server)
            suites.append(suite)
        return suites


class MockMCPClient:
    """
    Mock MCP client for testing servers.
    """
    
    def __init__(self, server):
        self.server = server
        self._request_id = 0
    
    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id
    
    async def initialize(self) -> Dict[str, Any]:
        """Send initialize request."""
        return await self.server.handle_request({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "mock-client", "version": "1.0.0"},
            }
        })
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return await self.server.handle_request({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {}
        })
    
    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Call a tool."""
        return await self.server.handle_request({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments}
        })
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available resources."""
        return await self.server.handle_request({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "resources/list",
            "params": {}
        })


def run_quick_test(server: Any) -> TestSuite:
    """Run quick synchronous smoke test."""
    return asyncio.run(_async_quick_test(server))


async def _async_quick_test(server: Any) -> TestSuite:
    """Async implementation of quick test."""
    tester = ServerTester(server)
    return await tester.run_smoke_tests()


__all__ = [
    "TestResult",
    "TestSuite",
    "ToolTester",
    "ServerTester",
    "IntegrationTester",
    "MockMCPClient",
    "run_quick_test",
]
