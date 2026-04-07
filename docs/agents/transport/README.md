# Agent Transport

**Module**: `codomyrmex.agents.transport` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Portable agent state serialization, HMAC-verified deserialization, wire-format protocol, and durable checkpointing. Enables agent state to be saved, transmitted, and restored across sessions and machines.

## Key Classes

| Class | Purpose |
|:---|:---|
| `AgentSerializer` | Serialize agent state to portable format |
| `AgentDeserializer` | Deserialize with HMAC integrity verification |
| `AgentSnapshot` | Complete agent state snapshot |
| `Checkpoint` | Durable checkpoint with delta tracking |
| `StateDelta` | Incremental state changes |
| `TransportMessage` | Wire-format message container |
| `MessageHeader` | Message metadata (type, timestamp, hmac) |
| `MessageType` | Message type enum (snapshot, delta, command) |
| `IntegrityError` | HMAC verification failure |

## Usage

```python
from codomyrmex.agents.transport import AgentSerializer

client = AgentSerializer()
```

## Source Module

Source: [`src/codomyrmex/agents/transport/`](../../../src/codomyrmex/agents/transport/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/transport/](../../../src/codomyrmex/agents/transport/)
- **Project Root**: [README.md](../../../README.md)
