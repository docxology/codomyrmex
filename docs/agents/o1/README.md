# O1/O3 (OpenAI Reasoning)

**Module**: `codomyrmex.agents.o1` | **Category**: API-based | **Last Updated**: March 2026

## Overview

OpenAI o1/o3 reasoning model integration. Supports extended thinking with chain-of-thought, reasoning token tracking, and superior multi-step problem solving.

## Purpose

OpenAI o1/o3 reasoning model integration for advanced multi-step reasoning tasks

## Source Module Structure

Source: [`src/codomyrmex/agents/o1/`](../../../../src/codomyrmex/agents/o1/)

### Key Files

| File | Purpose |
|:---|:---|
| [mcp_tools.py](../../../../src/codomyrmex/agents/o1/mcp_tools.py) |  ⭐ |
| [o1_client.py](../../../../src/codomyrmex/agents/o1/o1_client.py) |  ⭐ |

## Configuration

**Required API Key**: `OPENAI_API_KEY`

```bash
# Add to your .env or environment
OPENAI_API_KEY=your-key-here
```

## Quick Start

```python
from codomyrmex.agents.o1 import O1Client

client = O1Client()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [o1/README.md](../../../../src/codomyrmex/agents/o1/README.md) |
| SPEC | [o1/SPEC.md](../../../../src/codomyrmex/agents/o1/SPEC.md) |
| AGENTS | [o1/AGENTS.md](../../../../src/codomyrmex/agents/o1/AGENTS.md) |
| PAI | [o1/PAI.md](../../../../src/codomyrmex/agents/o1/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/o1/](../../../../src/codomyrmex/agents/o1/)
- **Project Root**: [README.md](../../../README.md)
