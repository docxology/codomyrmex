# Technical Specification - Streaming

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.llm.streaming`  
**Last Updated**: 2026-01-29

## 1. Purpose

Streaming response handlers for real-time LLM output processing

## 2. Architecture

### 2.1 Components

```
streaming/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `llm`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.llm.streaming
from codomyrmex.llm.streaming import (
    StreamEventType,           # Enum: START, DELTA, ERROR, END, TOOL_CALL, METADATA
    StreamEvent,               # Dataclass: event_type + content + delta + metadata + timestamp
    StreamStats,               # Dataclass: total_tokens, first_token_ms, total_duration_ms, tokens_per_second
    StreamBuffer,              # Thread-safe buffer accumulating streamed chunks with max_size guard
    StreamProcessor,           # ABC for stream event processors (process -> StreamEvent | None)
    PassthroughProcessor,      # No-op processor that passes events unchanged
    ContentFilterProcessor,    # Filters delta content matching block patterns
    JSONStreamParser,          # Incremental JSON object parser for streamed text
    StreamHandler,             # Main handler: iter_events(), process_stream(), callback registration
    stream_to_string,          # Convert an Iterator[str] to a complete string via StreamHandler
    chunk_stream,              # Generator splitting text into sized chunks with simulated delay (for testing)
)

# Key class signatures:
class StreamHandler:
    def add_processor(self, processor: StreamProcessor) -> StreamHandler: ...
    def on_delta(self, callback: Callable[[StreamEvent], None]) -> StreamHandler: ...
    def on_end(self, callback: Callable[[StreamEvent], None]) -> StreamHandler: ...
    def on_event(self, event_type: StreamEventType, callback: Callable[[StreamEvent], None]) -> StreamHandler: ...
    def iter_events(self, stream: Iterator[str], buffer_content: bool = True) -> Generator[StreamEvent, None, None]: ...
    def process_stream(self, stream: Iterator[str], buffer_content: bool = True) -> str: ...
    @property
    def buffer(self) -> StreamBuffer: ...
    @property
    def stats(self) -> StreamStats: ...

class JSONStreamParser:
    def feed(self, chunk: str) -> None: ...
    @property
    def has_complete_objects(self) -> bool: ...
    def get_objects(self) -> list[Any]: ...

def stream_to_string(stream: Iterator[str]) -> str: ...
def chunk_stream(text: str, chunk_size: int = 10) -> Generator[str, None, None]: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Processor pipeline pattern**: `StreamHandler` chains `StreamProcessor` instances; each processor can transform or filter events (returning `None` drops the event), enabling composable middleware.
2. **Thread-safe buffer with size guard**: `StreamBuffer` uses a threading lock and raises `ValueError` when accumulated content exceeds `max_size`, preventing unbounded memory growth.
3. **Callback-based and iterator-based consumption**: `StreamHandler` supports both `iter_events()` for pull-based consumption and `on_delta`/`on_end` callbacks for push-based consumption.

### 4.2 Limitations

- `JSONStreamParser` only handles top-level JSON objects (`{}`); top-level arrays are not detected.
- `StreamStats.total_tokens` approximates token count by whitespace-splitting deltas, not by a real tokenizer.
- `chunk_stream` includes a hardcoded 10 ms `time.sleep` per chunk; intended for testing only, not production use.

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/llm/streaming/
```

## 6. Future Considerations

- Add async stream support (`AsyncStreamHandler` with `async for` iteration)
- Support SSE (Server-Sent Events) parsing as a built-in `StreamProcessor`
- Add JSON array-level incremental parsing in `JSONStreamParser`
