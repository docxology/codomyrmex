"""Unit tests for WebSocketClient."""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from codomyrmex.networking.websocket_client import WebSocketClient

@pytest.mark.asyncio
async def test_websocket_client_on_handler():
    """Test the standardized .on() handler attachment."""
    client = WebSocketClient("ws://localhost:8080")
    
    # Mock handler
    handler = MagicMock()
    
    # Use the new .on() method
    client.on(handler)
    
    # Manually trigger message handling for testing
    await client._handle_message('{"test": "data"}')
    
    handler.assert_called_once_with({"test": "data"})

@pytest.mark.asyncio
async def test_websocket_client_on_async_handler():
    """Test the standardized .on() handler with async callback."""
    client = WebSocketClient("ws://localhost:8080")
    
    # Mock async handler
    handler_called = False
    async def async_handler(data):
        nonlocal handler_called
        handler_called = True
    
    # Use the new .on() method
    client.on(async_handler)
    
    # Manually trigger message handling
    await client._handle_message('{"test": "data"}')
    
    assert handler_called is True
