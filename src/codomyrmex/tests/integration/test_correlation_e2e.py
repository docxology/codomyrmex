"""End-to-end correlation ID context propagation tests.

Verifies that the correlation ID threads through programmatic invocations and MCP protocol layers down into the EventBus.
"""

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from codomyrmex.agents.pai.mcp_bridge import call_tool
from codomyrmex.events.core.event_bus import get_event_bus
from codomyrmex.logging_monitoring.correlation import (
    get_correlation_id,
    with_correlation,
)
from codomyrmex.model_context_protocol.server import MCPServer


@pytest.fixture
def clean_event_bus():
    """Provides a fresh, synchronous EventBus for testing."""
    bus = get_event_bus()
    # Ensure it is empty and synchronous for reliable assertions
    bus.subscriptions.clear()
    bus.reset_stats()
    
    # Optional: ensure we can intercept events
    events_caught = []
    bus.subscribe(["*"], lambda e: events_caught.append(e), subscriber_id="test_sub")
    
    yield bus, events_caught
    
    bus.unsubscribe("test_sub")


def test_call_tool_correlation(clean_event_bus):
    """Test that direct call_tool invocations generate and propagate a correlation ID."""
    bus, events = clean_event_bus

    # Mock tool to emit an event synchronously so we can observe the context
    def mock_tool_func():
        cid = get_correlation_id()
        # Create and publish a generic custom event
        from codomyrmex.events.core.event_schema import Event, EventType
        evt = Event(event_type=EventType.CUSTOM, source="mock_tool")
        bus.publish(evt)
        return {"invoked_cid": cid}

    with patch("codomyrmex.agents.pai.trust_gateway.trusted_call_tool", side_effect=lambda *a, **kw: mock_tool_func()):
        result = call_tool("mock.tool")

    # The tool should have been assigned a correlation ID by the wrapper
    invoked_cid = result.get("invoked_cid")
    assert invoked_cid is not None
    assert invoked_cid != ""

    # The EventBus should have intercepted the event and stamped it with the active CID
    assert len(events) == 1
    emitted_event = events[0]
    assert emitted_event.correlation_id == invoked_cid


@pytest.mark.asyncio
async def test_mcp_server_http_correlation(clean_event_bus):
    """Test that MCPServer HTTP transport accepts and propagates X-Correlation-ID."""
    bus, events = clean_event_bus
    
    import uvicorn
    import fastapi
    
    # Create the app (normally done inside run_http, but we test the route logic here)
    server = MCPServer()
    
    # We mock _call_tool to simply return the current correlation ID
    async def mock_call_tool(params):
        cid = get_correlation_id()
        # Emit event to test EventBus
        from codomyrmex.events.core.event_schema import Event, EventType
        bus.publish(Event(event_type=EventType.CUSTOM, source="http_test"))
        return {"observed_cid": cid}
        
    server._call_tool = mock_call_tool
    
    # Since run_http encapsulates the FastAPI setup, we'll manually instantiate 
    # the router endpoint logic to unit-test the HTTP-to-MCP translation
    from fastapi import Request
    from fastapi.responses import JSONResponse
    
    async def mcp_endpoint(request: Request):
        body = await request.json()
        cid = request.headers.get("x-correlation-id") or request.headers.get("X-Correlation-ID")
        response = await server.handle_request(body, correlation_id=cid)
        
        headers = {}
        if cid:
            headers["X-Correlation-ID"] = cid
            
        if response is None:
            return JSONResponse(content={"status": "accepted"}, status_code=202, headers=headers)
        return JSONResponse(content=response, headers=headers)
    
    
    async def get_mock_json():
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "test"}
        }

    # Create a quick mock Request object
    mock_request = MagicMock()
    mock_request.json = get_mock_json
    
    # Provide our test header
    test_cid = "test-cid-123"
    mock_request.headers = {"x-correlation-id": test_cid}
    
    # Execute the endpoint handler
    response = await mcp_endpoint(mock_request)
    
    # 1. The HTTP response headers should echo the CID
    assert response.headers.get("X-Correlation-ID") == test_cid
    
    # 2. The result content should prove the MCP Context tracked the CID
    body = json.loads(response.body)
    assert body["result"]["observed_cid"] == test_cid
    
    # 3. The EventBus should have caught an event implicitly stamped with the CID
    assert len(events) == 1
    assert events[0].correlation_id == test_cid
