# streaming

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Streaming response handlers for LLM outputs. Provides a complete toolkit for consuming, buffering, processing, and parsing streamed LLM responses in real time, including event-driven callbacks, pluggable processor pipelines, incremental JSON parsing, and throughput statistics tracking.

## Key Exports

- **`StreamEventType`** -- Enum of streaming event types: START, DELTA, ERROR, END, TOOL_CALL, METADATA
- **`StreamEvent`** -- Dataclass representing a single streaming event with type, content delta, metadata, and timestamp
- **`StreamStats`** -- Dataclass tracking stream statistics: total tokens, first-token latency, duration, and tokens-per-second
- **`StreamBuffer`** -- Thread-safe buffer for accumulating streamed content chunks with configurable max size
- **`StreamProcessor`** -- Abstract base class for stream event processors (filter/transform pipeline stages)
- **`PassthroughProcessor`** -- StreamProcessor that passes all events through unchanged
- **`ContentFilterProcessor`** -- StreamProcessor that replaces delta content matching block patterns with "[FILTERED]"
- **`JSONStreamParser`** -- Incremental JSON parser that extracts complete JSON objects from a character stream
- **`StreamHandler`** -- Main stream handler: iterates events, applies processors, buffers content, collects stats, and dispatches callbacks
- **`stream_to_string()`** -- Convenience function to consume an entire stream iterator and return the concatenated string
- **`chunk_stream()`** -- Utility generator that splits text into fixed-size chunks with simulated delay (useful for testing)

## Directory Contents

- `__init__.py` - All streaming classes, enums, dataclasses, and utility functions
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [llm](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
