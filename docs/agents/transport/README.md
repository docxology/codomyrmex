# Agent Transport & Serialization

**Module**: `codomyrmex.agents.transport` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Portable agent state serialization, HMAC-verified deserialization, wire-format messaging protocol, and durable checkpoint persistence. Enables agent state transfer across process boundaries.

## Purpose

Portable agent state serialization, HMAC-verified deserialization, wire-format messaging protocol, and durable checkpoint persistence. Enables agent state to be saved, transmitted, verified, and restored across process boundaries.

## Source Module Structure

Source: [`src/codomyrmex/agents/transport/`](../../../../src/codomyrmex/agents/transport/)

### Key Files

| File | Purpose |
|:---|:---|
| [checkpoint.py](../../../../src/codomyrmex/agents/transport/checkpoint.py) |  ⭐ |
| [deserializer.py](../../../../src/codomyrmex/agents/transport/deserializer.py) |  ⭐ |
| [protocol.py](../../../../src/codomyrmex/agents/transport/protocol.py) |  ⭐ |
| [serializer.py](../../../../src/codomyrmex/agents/transport/serializer.py) |  ⭐ |

## Quick Start

```python
from codomyrmex.agents.transport import TransportClient

client = TransportClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [transport/README.md](../../../../src/codomyrmex/agents/transport/README.md) |
| SPEC | [transport/SPEC.md](../../../../src/codomyrmex/agents/transport/SPEC.md) |
| AGENTS | [transport/AGENTS.md](../../../../src/codomyrmex/agents/transport/AGENTS.md) |
| PAI | [transport/PAI.md](../../../../src/codomyrmex/agents/transport/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/transport/](../../../../src/codomyrmex/agents/transport/)
- **Project Root**: [README.md](../../../README.md)
