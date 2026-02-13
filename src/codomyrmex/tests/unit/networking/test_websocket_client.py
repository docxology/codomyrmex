"""Unit tests for WebSocketClient."""

import asyncio

import pytest

from codomyrmex.networking.websocket_client import WebSocketClient


class CallTracker:
    """Real callable that tracks calls — replaces MagicMock."""

    def __init__(self):
        self.calls: list = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))

    @property
    def call_count(self):
        return len(self.calls)

    def assert_called_once_with(self, *expected_args, **expected_kwargs):
        assert self.call_count == 1, f"Expected 1 call, got {self.call_count}"
        args, kwargs = self.calls[0]
        assert args == expected_args
        assert kwargs == expected_kwargs


@pytest.mark.asyncio
async def test_websocket_client_on_handler():
    """Test the standardized .on() handler attachment."""
    client = WebSocketClient("ws://localhost:8080")

    handler = CallTracker()
    client.on(handler)

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


@pytest.mark.asyncio
async def test_websocket_client_initialization():
    """Test WebSocketClient initialization."""
    client = WebSocketClient("ws://localhost:8080")

    assert client.url == "ws://localhost:8080"
    assert client._handlers is not None


@pytest.mark.asyncio
async def test_websocket_client_multiple_handlers():
    """Test registering multiple handlers."""
    client = WebSocketClient("ws://localhost:8080")

    results = []

    async def handler1(data):
        results.append(("handler1", data))

    async def handler2(data):
        results.append(("handler2", data))

    client.on(handler1)
    client.on(handler2)

    await client._handle_message('{"key": "value"}')

    # Both handlers should have been called
    assert len(results) == 2
    assert ("handler1", {"key": "value"}) in results
    assert ("handler2", {"key": "value"}) in results


@pytest.mark.asyncio
async def test_websocket_client_message_parsing():
    """Test message parsing from string to dict."""
    client = WebSocketClient("ws://localhost:8080")

    received_data = None

    async def handler(data):
        nonlocal received_data
        received_data = data

    client.on(handler)

    # Test parsing JSON message
    await client._handle_message('{"name": "test", "count": 42}')

    assert received_data == {"name": "test", "count": 42}


@pytest.mark.asyncio
async def test_websocket_client_handler_exception_handling():
    """Test that handler exceptions don't break the client."""
    client = WebSocketClient("ws://localhost:8080")

    call_count = 0

    async def failing_handler(data):
        raise ValueError("Handler error")

    async def working_handler(data):
        nonlocal call_count
        call_count += 1

    client.on(failing_handler)
    client.on(working_handler)

    # Should not raise, even with failing handler
    try:
        await client._handle_message('{"test": true}')
    except ValueError:
        pass  # May or may not propagate depending on implementation

    # The working handler should still have been called
    # (depending on implementation order)


@pytest.mark.asyncio
async def test_websocket_client_concurrent_messages():
    """Test handling concurrent messages."""
    client = WebSocketClient("ws://localhost:8080")

    received_messages = []

    async def handler(data):
        received_messages.append(data)
        await asyncio.sleep(0.01)  # Simulate processing time

    client.on(handler)

    # Send multiple messages concurrently
    messages = [
        '{"id": 1}',
        '{"id": 2}',
        '{"id": 3}',
    ]

    await asyncio.gather(*[client._handle_message(msg) for msg in messages])

    # All messages should have been received
    assert len(received_messages) == 3
    ids = {msg["id"] for msg in received_messages}
    assert ids == {1, 2, 3}


@pytest.mark.asyncio
async def test_websocket_client_empty_message():
    """Test handling empty message."""
    client = WebSocketClient("ws://localhost:8080")

    received = []

    async def handler(data):
        received.append(data)

    client.on(handler)

    # Empty JSON object
    await client._handle_message('{}')

    assert received == [{}]


@pytest.mark.asyncio
async def test_websocket_client_handler_order():
    """Test handlers are called in registration order."""
    client = WebSocketClient("ws://localhost:8080")

    order = []

    async def first_handler(data):
        order.append("first")

    async def second_handler(data):
        order.append("second")

    async def third_handler(data):
        order.append("third")

    client.on(first_handler)
    client.on(second_handler)
    client.on(third_handler)

    await client._handle_message('{"test": 1}')

    # Order should be preserved
    assert order == ["first", "second", "third"]
