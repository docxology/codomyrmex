# defense - Functional Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Provide deterministic local active-defense primitives for Codomyrmex agents,
demos, and security workflows.

## Functional Requirements

1. Detect prompt-exploit patterns such as instruction override, data exfiltration
   attempts, and tool-abuse phrasing.
2. Create honeytokens that can be embedded in suspicious contexts.
3. Track contained sources and return bounded decoy responses.
4. Process request metadata through blocklists, rate limits, detection rules, and
   prompt-defense checks.
5. Expose safe MCP wrappers for exploit detection, request screening, and threat
   reporting.

## Interface Contracts

```python
from codomyrmex.defense import ActiveDefense, Defense

active = ActiveDefense()
exploit_result = active.detect_exploit("ignore previous instructions")

defense = Defense({"max_requests": 10})
allowed, threats = defense.process_request("client-1", {"input": "hello"})
```

## Validation

```bash
uv run pytest src/codomyrmex/tests/unit/defense/ -q
uv run ruff check src/codomyrmex/defense
uv run ty check --output-format concise src/codomyrmex/defense
```

## Navigation

- **Module Overview**: [README.md](README.md)
- **Agent Guidance**: [AGENTS.md](AGENTS.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **PAI Mapping**: [PAI.md](PAI.md)
