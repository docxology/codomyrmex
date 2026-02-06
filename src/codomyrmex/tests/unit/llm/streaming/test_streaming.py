"""
Tests for LLM Streaming Module
"""


import pytest

from codomyrmex.llm.streaming import (
    ContentFilterProcessor,
    JSONStreamParser,
    StreamBuffer,
    StreamEvent,
    StreamEventType,
    StreamHandler,
    chunk_stream,
    stream_to_string,
)


class TestStreamEvent:
    """Tests for StreamEvent."""

    def test_create(self):
        """Should create stream event."""
        event = StreamEvent(event_type=StreamEventType.DELTA, delta="Hello")
        assert event.delta == "Hello"

    def test_is_content(self):
        """Should identify content events."""
        delta = StreamEvent(event_type=StreamEventType.DELTA, delta="text")
        start = StreamEvent(event_type=StreamEventType.START)

        assert delta.is_content
        assert not start.is_content


class TestStreamBuffer:
    """Tests for StreamBuffer."""

    def test_append(self):
        """Should append chunks."""
        buffer = StreamBuffer()
        buffer.append("Hello ")
        buffer.append("World")

        assert buffer.content == "Hello World"

    def test_length(self):
        """Should track length."""
        buffer = StreamBuffer()
        buffer.append("12345")

        assert buffer.length == 5
        assert buffer.chunk_count == 1

    def test_max_size(self):
        """Should enforce max size."""
        buffer = StreamBuffer(max_size=10)
        buffer.append("12345")

        with pytest.raises(ValueError):
            buffer.append("67890extra")

    def test_clear(self):
        """Should clear buffer."""
        buffer = StreamBuffer()
        buffer.append("test")
        buffer.clear()

        assert buffer.content == ""
        assert buffer.length == 0


class TestContentFilterProcessor:
    """Tests for ContentFilterProcessor."""

    def test_filter_blocked(self):
        """Should filter blocked patterns."""
        proc = ContentFilterProcessor(block_patterns=["password"])
        event = StreamEvent(event_type=StreamEventType.DELTA, delta="my password is 123")

        result = proc.process(event)

        assert result.delta == "[FILTERED]"

    def test_pass_allowed(self):
        """Should pass allowed content."""
        proc = ContentFilterProcessor(block_patterns=["secret"])
        event = StreamEvent(event_type=StreamEventType.DELTA, delta="normal text")

        result = proc.process(event)

        assert result.delta == "normal text"


class TestJSONStreamParser:
    """Tests for JSONStreamParser."""

    def test_parse_complete(self):
        """Should parse complete JSON."""
        parser = JSONStreamParser()
        parser.feed('{"name": "test"}')

        assert parser.has_complete_objects
        objs = parser.get_objects()
        assert objs[0]["name"] == "test"

    def test_parse_partial(self):
        """Should handle partial JSON."""
        parser = JSONStreamParser()
        parser.feed('{"name"')

        assert not parser.has_complete_objects

        parser.feed(': "test"}')
        assert parser.has_complete_objects

    def test_parse_multiple(self):
        """Should parse multiple objects."""
        parser = JSONStreamParser()
        parser.feed('{"a": 1}{"b": 2}')

        objs = parser.get_objects()
        assert len(objs) == 2


class TestStreamHandler:
    """Tests for StreamHandler."""

    def test_iter_events(self):
        """Should iterate over events."""
        handler = StreamHandler()
        stream = iter(["Hello", " ", "World"])

        events = list(handler.iter_events(stream))

        # Start + 3 deltas + end
        assert len(events) == 5

    def test_buffer_content(self):
        """Should buffer content."""
        handler = StreamHandler()
        stream = iter(["Hello", " ", "World"])

        list(handler.iter_events(stream))

        assert handler.buffer.content == "Hello World"

    def test_stats(self):
        """Should track stats."""
        handler = StreamHandler()
        stream = iter(["a", "b", "c"])

        list(handler.iter_events(stream))

        assert handler.stats.events_count == 3

    def test_process_stream(self):
        """Should process entire stream."""
        handler = StreamHandler()

        result = handler.process_stream(iter(["Hello", " World"]))

        assert result == "Hello World"

    def test_callbacks(self):
        """Should call callbacks."""
        handler = StreamHandler()
        deltas = []

        handler.on_delta(lambda e: deltas.append(e.delta))
        handler.process_stream(iter(["a", "b"]))

        assert deltas == ["a", "b"]


class TestUtilities:
    """Tests for utility functions."""

    def test_stream_to_string(self):
        """Should convert stream to string."""
        result = stream_to_string(iter(["Hello", " ", "World"]))
        assert result == "Hello World"

    def test_chunk_stream(self):
        """Should chunk text."""
        chunks = list(chunk_stream("Hello World", chunk_size=5))
        assert chunks == ["Hello", " Worl", "d"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
