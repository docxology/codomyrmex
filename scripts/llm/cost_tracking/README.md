# Cost Tracking Scripts

**Module**: scripts/llm/cost_tracking  
**Status**: Active

## Overview

Scripts for token counting and LLM API cost estimation.

## Scripts

| Script | API Required | Description |
|--------|-------------|-------------|
| `cost_tracking_demo.py` | No | Simulated cost estimation demo |
| `openrouter_free_example.py` | Yes | Real cost tracking with OpenRouter |

## Quick Start

```bash
# Demo (no API key required)
python cost_tracking_demo.py

# Live example (requires API key)
export OPENROUTER_API_KEY='your-key-here'
python openrouter_free_example.py
```

## Features Demonstrated

- Token counting (prompt + completion)
- Cost estimation for different models
- Usage tracking across multiple requests
- Free model ($0 cost) for development

## Navigation

- **Parent**: [scripts/llm](../README.md)
