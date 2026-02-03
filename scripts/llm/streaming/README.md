# Streaming Scripts

**Module**: scripts/llm/streaming  
**Status**: Active

## Overview

Scripts for real-time streaming LLM response handling.

## Scripts

| Script | API Required | Description |
|--------|-------------|-------------|
| `streaming_demo.py` | No | Simulated streaming patterns demo |
| `openrouter_free_example.py` | Yes | Real streaming with OpenRouter |

## Quick Start

```bash
# Demo (no API key required)
python streaming_demo.py

# Live example (requires API key)
export OPENROUTER_API_KEY='your-key-here'
python openrouter_free_example.py
```

## Features Demonstrated

- Token-by-token output
- Buffered streaming
- Progress indicators
- Real-time processing
- Error handling during streams

## Navigation

- **Parent**: [scripts/llm](../README.md)
