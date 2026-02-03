# Guardrails Scripts

**Module**: scripts/llm/guardrails  
**Status**: Active

## Overview

Scripts for LLM input/output safety validation and prompt injection defense.

## Scripts

| Script | API Required | Description |
|--------|-------------|-------------|
| `guardrails_demo.py` | No | Comprehensive safety pattern demo |
| `openrouter_free_example.py` | Yes | Real input validation with OpenRouter |

## Quick Start

```bash
# Demo (no API key required)
python guardrails_demo.py

# Live example (requires API key)
export OPENROUTER_API_KEY='your-key-here'
python openrouter_free_example.py
```

## Features Demonstrated

- Prompt injection detection
- Input sanitization
- Harmful content filtering
- Output validation
- PII leak detection
- Role hijacking prevention

## Navigation

- **Parent**: [scripts/llm](../README.md)
