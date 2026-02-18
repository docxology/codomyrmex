"""Tests for streaming.async_stream module."""

import asyncio

import pytest

try:
    from codomyrmex.events.streaming import Event, EventType
    from codomyrmex.events.streaming.async_stream import (
        AsyncStream,
        BatchingStream,
        WebSocketStream,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("streaming.async_stream module not available", allow_module_level=True)


def _run(coro):
    """Helper to run async code in sync tests."""
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# AsyncStream
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAsyncStream:
    def test_create(self):
        stream = AsyncStream(buffer_size=100)
        assert stream._running is False

    def test_create_with_backpressure(self):
        stream = AsyncStream(buffer_size=50, enable_backpressure=True)
        assert stream._buffer.maxsize == 50

    def test_create_without_backpressure(self):
        stream = AsyncStream(buffer_size=50, enable_backpressure=False)
        assert stream._buffer.maxsize == 0  # Unlimited

    def test_start_stop(self):
        async def _test():
            stream = AsyncStream()
            await stream.start()
            assert stream._running is True
            await stream.stop()
            assert stream._running is False
        _run(_test())

    def test_subscribe(self):
        async def _test():
            stream = AsyncStream()
            sub_id = await stream.subscribe()
            assert sub_id is not None
            assert isinstance(sub_id, str)
            assert sub_id in stream._subscribers
        _run(_test())

    def test_unsubscribe(self):
        async def _test():
            stream = AsyncStream()
            sub_id = await stream.subscribe()
            result = await stream.unsubscribe(sub_id)
            assert result is True
            assert sub_id not in stream._subscribers
        _run(_test())

    def test_unsubscribe_nonexistent(self):
        async def _test():
            stream = AsyncStream()
            result = await stream.unsubscribe("nonexistent")
            assert result is False
        _run(_test())

    def test_publish(self):
        async def _test():
            stream = AsyncStream()
            event = Event(type=EventType.MESSAGE, data="hello")
            result = await stream.publish(event)
            assert result is True
        _run(_test())

    def test_subscribe_custom_buffer(self):
        async def _test():
            stream = AsyncStream()
            sub_id = await stream.subscribe(buffer_size=50)
            assert stream._subscribers[sub_id].maxsize == 50
        _run(_test())

    def test_multiple_subscribers(self):
        async def _test():
            stream = AsyncStream()
            sub1 = await stream.subscribe()
            sub2 = await stream.subscribe()
            assert sub1 != sub2
            assert len(stream._subscribers) == 2
        _run(_test())

    def test_broadcast_to_subscribers(self):
        async def _test():
            stream = AsyncStream()
            sub_id = await stream.subscribe()
            event = Event(type=EventType.MESSAGE, data="test")
            await stream._broadcast(event)
            queue = stream._subscribers[sub_id]
            assert not queue.empty()
            received = queue.get_nowait()
            assert received.data == "test"
        _run(_test())


# ---------------------------------------------------------------------------
# WebSocketStream
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestWebSocketStream:
    def test_create(self):
        ws_stream = WebSocketStream()
        assert ws_stream._connections == {}

    def test_connect(self):
        async def _test():
            ws_stream = WebSocketStream()

            class MockWebSocket:
                async def send(self, data):
                    pass

            ws = MockWebSocket()
            sub_id = await ws_stream.connect(ws, "client1")
            assert sub_id is not None
            assert "client1" in ws_stream._connections
        _run(_test())

    def test_disconnect(self):
        async def _test():
            ws_stream = WebSocketStream()

            class MockWebSocket:
                async def send(self, data):
                    pass

            ws = MockWebSocket()
            await ws_stream.connect(ws, "client1")
            await ws_stream.disconnect("client1")
            assert "client1" not in ws_stream._connections
        _run(_test())

    def test_disconnect_nonexistent(self):
        async def _test():
            ws_stream = WebSocketStream()
            await ws_stream.disconnect("nonexistent")
        _run(_test())

    def test_send_to_nonexistent(self):
        async def _test():
            ws_stream = WebSocketStream()
            event = Event(type=EventType.MESSAGE, data="hello")
            result = await ws_stream.send_to("nonexistent", event)
            assert result is False
        _run(_test())

    def test_send_to_connected(self):
        async def _test():
            ws_stream = WebSocketStream()
            sent_data = []

            class MockWebSocket:
                async def send(self, data):
                    sent_data.append(data)

            ws = MockWebSocket()
            await ws_stream.connect(ws, "client1")
            event = Event(type=EventType.MESSAGE, data="hello")
            result = await ws_stream.send_to("client1", event)
            assert result is True
            assert len(sent_data) == 1
        _run(_test())

    def test_send_to_failing_ws(self):
        async def _test():
            ws_stream = WebSocketStream()

            class FailingWebSocket:
                async def send(self, data):
                    raise ConnectionError("Connection lost")

            ws = FailingWebSocket()
            await ws_stream.connect(ws, "client1")
            event = Event(type=EventType.MESSAGE, data="hello")
            result = await ws_stream.send_to("client1", event)
            assert result is False
        _run(_test())


# ---------------------------------------------------------------------------
# BatchingStream
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBatchingStream:
    def test_create(self):
        stream = BatchingStream(batch_size=100, flush_interval=1.0)
        assert stream._batch_size == 100
        assert stream._flush_interval == 1.0
        assert stream._running is False

    def test_add_event(self):
        async def _test():
            stream = BatchingStream(batch_size=100)
            event = Event(type=EventType.MESSAGE, data="test")
            await stream.add(event)
            assert len(stream._batch) == 1
        _run(_test())

    def test_on_batch_handler(self):
        async def _test():
            batches_received = []
            stream = BatchingStream(batch_size=2)
            stream.on_batch(lambda batch: batches_received.append(batch))

            await stream.add(Event(type=EventType.MESSAGE, data="one"))
            await stream.add(Event(type=EventType.MESSAGE, data="two"))

            assert len(batches_received) == 1
            assert len(batches_received[0]) == 2
        _run(_test())

    def test_flush_empties_batch(self):
        async def _test():
            stream = BatchingStream(batch_size=100)
            await stream.add(Event(type=EventType.MESSAGE, data="test"))
            assert len(stream._batch) == 1
            await stream._flush()
            assert len(stream._batch) == 0
        _run(_test())

    def test_flush_empty_batch_noop(self):
        async def _test():
            stream = BatchingStream()
            await stream._flush()
        _run(_test())

    def test_start_stop(self):
        async def _test():
            stream = BatchingStream(flush_interval=0.05)
            await stream.start()
            assert stream._running is True
            await stream.stop()
            assert stream._running is False
        _run(_test())

    def test_stop_flushes_remaining(self):
        async def _test():
            flushed = []
            stream = BatchingStream(batch_size=100, flush_interval=10.0)
            stream.on_batch(lambda batch: flushed.append(batch))
            await stream.add(Event(type=EventType.MESSAGE, data="remaining"))
            await stream.stop()
            assert len(flushed) == 1
        _run(_test())

    def test_multiple_handlers(self):
        async def _test():
            handler1_calls = []
            handler2_calls = []
            stream = BatchingStream(batch_size=100)
            stream.on_batch(lambda batch: handler1_calls.append(len(batch)))
            stream.on_batch(lambda batch: handler2_calls.append(len(batch)))

            await stream.add(Event(type=EventType.MESSAGE, data="test"))
            await stream._flush()

            assert len(handler1_calls) == 1
            assert len(handler2_calls) == 1
        _run(_test())
