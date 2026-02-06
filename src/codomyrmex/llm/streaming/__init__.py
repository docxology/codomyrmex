"""
LLM Streaming Module

Streaming response handlers for LLM outputs.
"""

__version__ = "0.1.0"

import json
import queue
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from collections.abc import Callable, Generator, Iterator


class StreamEventType(Enum):
    """Types of streaming events."""
    START = "start"
    DELTA = "delta"
    ERROR = "error"
    END = "end"
    TOOL_CALL = "tool_call"
    METADATA = "metadata"


@dataclass
class StreamEvent:
    """A single streaming event."""
    event_type: StreamEventType
    content: str = ""
    delta: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_content(self) -> bool:
        """Check if event contains content."""
        return self.event_type == StreamEventType.DELTA and bool(self.delta)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.event_type.value,
            "content": self.content,
            "delta": self.delta,
            "metadata": self.metadata,
        }


@dataclass
class StreamStats:
    """Statistics for a stream."""
    total_tokens: int = 0
    first_token_ms: float = 0.0
    total_duration_ms: float = 0.0
    events_count: int = 0

    @property
    def tokens_per_second(self) -> float:
        """Calculate tokens per second."""
        if self.total_duration_ms == 0:
            return 0.0
        return self.total_tokens / (self.total_duration_ms / 1000)


class StreamBuffer:
    """
    Buffer for accumulating streamed content.

    Usage:
        buffer = StreamBuffer()

        for chunk in stream:
            buffer.append(chunk)
            print(chunk, end="", flush=True)

        full_response = buffer.content
    """

    def __init__(self, max_size: int = 100000):
        self.max_size = max_size
        self._chunks: list[str] = []
        self._total_length = 0
        self._lock = threading.Lock()

    def append(self, chunk: str) -> None:
        """Append a chunk to the buffer."""
        with self._lock:
            if self._total_length + len(chunk) > self.max_size:
                raise ValueError(f"Buffer size exceeded: {self.max_size}")
            self._chunks.append(chunk)
            self._total_length += len(chunk)

    @property
    def content(self) -> str:
        """Get full buffered content."""
        with self._lock:
            return "".join(self._chunks)

    @property
    def length(self) -> int:
        """Get current content length."""
        return self._total_length

    @property
    def chunk_count(self) -> int:
        """Get number of chunks."""
        return len(self._chunks)

    def clear(self) -> None:
        """Clear the buffer."""
        with self._lock:
            self._chunks.clear()
            self._total_length = 0


class StreamProcessor(ABC):
    """Base class for stream processors."""

    @abstractmethod
    def process(self, event: StreamEvent) -> StreamEvent | None:
        """Process a stream event. Return None to filter out."""
        pass


class PassthroughProcessor(StreamProcessor):
    """Passes events through unchanged."""

    def process(self, event: StreamEvent) -> StreamEvent | None:
        return event


class ContentFilterProcessor(StreamProcessor):
    """Filters content based on patterns."""

    def __init__(self, block_patterns: list[str] | None = None):
        self.block_patterns = block_patterns or []

    def process(self, event: StreamEvent) -> StreamEvent | None:
        if event.event_type == StreamEventType.DELTA:
            for pattern in self.block_patterns:
                if pattern.lower() in event.delta.lower():
                    return StreamEvent(
                        event_type=StreamEventType.DELTA,
                        delta="[FILTERED]",
                    )
        return event


class JSONStreamParser:
    """
    Parses JSON from a stream incrementally.

    Usage:
        parser = JSONStreamParser()

        for chunk in stream:
            parser.feed(chunk)
            if parser.has_complete_objects:
                for obj in parser.get_objects():
                    print(obj)
    """

    def __init__(self):
        self._buffer = ""
        self._objects: list[Any] = []
        self._depth = 0
        self._in_string = False
        self._escape_next = False

    def feed(self, chunk: str) -> None:
        """Feed a chunk of text."""
        for char in chunk:
            self._buffer += char

            if self._escape_next:
                self._escape_next = False
                continue

            if char == '\\' and self._in_string:
                self._escape_next = True
                continue

            if char == '"' and not self._escape_next:
                self._in_string = not self._in_string
                continue

            if not self._in_string:
                if char == '{':
                    if self._depth == 0:
                        self._buffer = char
                    self._depth += 1
                elif char == '}':
                    self._depth -= 1
                    if self._depth == 0:
                        try:
                            obj = json.loads(self._buffer)
                            self._objects.append(obj)
                            self._buffer = ""
                        except json.JSONDecodeError:
                            pass

    @property
    def has_complete_objects(self) -> bool:
        """Check if complete objects are available."""
        return len(self._objects) > 0

    def get_objects(self) -> list[Any]:
        """Get and clear complete objects."""
        objects = self._objects
        self._objects = []
        return objects

    def reset(self) -> None:
        """Reset parser state."""
        self._buffer = ""
        self._objects = []
        self._depth = 0
        self._in_string = False


class StreamHandler:
    """
    Main stream handler for LLM responses.

    Usage:
        handler = StreamHandler()

        # Sync iteration
        for event in handler.iter_events(response_stream):
            if event.is_content:
                print(event.delta, end="")

        # With callbacks
        handler.on_delta(lambda e: print(e.delta, end=""))
        handler.process_stream(response_stream)
    """

    def __init__(self):
        self._processors: list[StreamProcessor] = []
        self._callbacks: dict[StreamEventType, list[Callable]] = {}
        self._buffer = StreamBuffer()
        self._stats = StreamStats()

    def add_processor(self, processor: StreamProcessor) -> "StreamHandler":
        """Add a stream processor."""
        self._processors.append(processor)
        return self

    def on_event(self, event_type: StreamEventType, callback: Callable[[StreamEvent], None]) -> "StreamHandler":
        """Register a callback for an event type."""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)
        return self

    def on_delta(self, callback: Callable[[StreamEvent], None]) -> "StreamHandler":
        """Register a callback for delta events."""
        return self.on_event(StreamEventType.DELTA, callback)

    def on_end(self, callback: Callable[[StreamEvent], None]) -> "StreamHandler":
        """Register a callback for end events."""
        return self.on_event(StreamEventType.END, callback)

    def _process_event(self, event: StreamEvent) -> StreamEvent | None:
        """Process event through all processors."""
        current = event
        for processor in self._processors:
            current = processor.process(current)
            if current is None:
                return None
        return current

    def _emit(self, event: StreamEvent) -> None:
        """Emit event to callbacks."""
        callbacks = self._callbacks.get(event.event_type, [])
        for callback in callbacks:
            try:
                callback(event)
            except Exception:
                pass

    def iter_events(
        self,
        stream: Iterator[str],
        buffer_content: bool = True,
    ) -> Generator[StreamEvent, None, None]:
        """
        Iterate over stream events.

        Args:
            stream: Iterator of string chunks
            buffer_content: Whether to buffer content

        Yields:
            StreamEvent for each chunk
        """
        start_time = time.time()
        first_token = True

        # Emit start
        start_event = StreamEvent(event_type=StreamEventType.START)
        yield start_event

        for chunk in stream:
            if first_token:
                self._stats.first_token_ms = (time.time() - start_time) * 1000
                first_token = False

            event = StreamEvent(
                event_type=StreamEventType.DELTA,
                delta=chunk,
            )

            processed = self._process_event(event)
            if processed:
                if buffer_content:
                    self._buffer.append(processed.delta)

                self._stats.events_count += 1
                self._stats.total_tokens += len(processed.delta.split())

                yield processed

        self._stats.total_duration_ms = (time.time() - start_time) * 1000

        # Emit end
        end_event = StreamEvent(
            event_type=StreamEventType.END,
            content=self._buffer.content,
        )
        yield end_event

    def process_stream(
        self,
        stream: Iterator[str],
        buffer_content: bool = True,
    ) -> str:
        """
        Process entire stream and return content.

        Args:
            stream: Iterator of string chunks
            buffer_content: Whether to buffer content

        Returns:
            Complete content string
        """
        for event in self.iter_events(stream, buffer_content):
            self._emit(event)

        return self._buffer.content

    @property
    def buffer(self) -> StreamBuffer:
        """Get the content buffer."""
        return self._buffer

    @property
    def stats(self) -> StreamStats:
        """Get stream statistics."""
        return self._stats


def stream_to_string(stream: Iterator[str]) -> str:
    """Convert a stream to a complete string."""
    handler = StreamHandler()
    return handler.process_stream(stream)


def chunk_stream(text: str, chunk_size: int = 10) -> Generator[str, None, None]:
    """Generate chunks from text (for testing)."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]
        time.sleep(0.01)  # Simulate network delay


__all__ = [
    # Enums
    "StreamEventType",
    # Data classes
    "StreamEvent",
    "StreamStats",
    # Components
    "StreamBuffer",
    "StreamProcessor",
    "PassthroughProcessor",
    "ContentFilterProcessor",
    "JSONStreamParser",
    # Core
    "StreamHandler",
    # Utilities
    "stream_to_string",
    "chunk_stream",
]
