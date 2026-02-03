# Prompts Scripts

**Module**: scripts/llm/prompts  
**Status**: Active

## Overview

Scripts for prompt template management, versioning, and rendering.

## Scripts

| Script | API Required | Description |
|--------|-------------|-------------|
| `prompts_demo.py` | No | Template library and versioning demo |
| `openrouter_free_example.py` | Yes | Real template usage with OpenRouter |

## Quick Start

```bash
# Demo (no API key required)
python prompts_demo.py

# Live example (requires API key)
export OPENROUTER_API_KEY='your-key-here'
python openrouter_free_example.py
```

## Features Demonstrated

- Prompt template loading
- Variable substitution
- Template validation
- Version management
- Reusable prompt library

## Navigation

- **Parent**: [scripts/llm](../README.md)
