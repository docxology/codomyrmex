# defense

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

The defense module provides local active-defense primitives for prompt-exploit
detection, honeytokens, context poisoning, rate limiting, threat rules, and
rabbit-hole containment. It is a compatibility package used by demos, security
docs, MCP tools, and the AI-safety facade.

## Key Components

| Component | File | Purpose |
| :--- | :--- | :--- |
| `ActiveDefense` | `active.py` | Detects prompt-exploit patterns, creates honeytokens, and emits threat reports |
| `RabbitHole` | `active.py` / `rabbithole.py` | Tracks contained sources and returns decoy responses |
| `Defense` | `defense.py` | Orchestrates blocklist, rate-limit, rule, and prompt-defense checks |
| `RateLimiter` | `defense.py` | Sliding-window request limiter |
| `ThreatDetector` | `defense.py` | Rule engine for `DetectionRule` objects |
| `mcp_tools.py` | `mcp_tools.py` | MCP wrappers for exploit detection, request processing, and reports |

## Quick Start

```python
from codomyrmex.defense import ActiveDefense, Defense

active = ActiveDefense()
result = active.detect_exploit("ignore previous instructions")

defense = Defense({"max_requests": 10})
allowed, threats = defense.process_request("client-1", {"input": "hello"})
```

## Validation

```bash
uv run pytest tests/unit/defense/ -q
uv run ruff check src/codomyrmex/defense
uv run ty check --output-format concise src/codomyrmex/defense
```

## Navigation

- **Agent Guidance**: [AGENTS.md](AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
