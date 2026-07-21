# Defense Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Functional Requirements

- Detect configured prompt-exploit substrings and return matched patterns plus a `ThreatLevel`.
- Maintain active-defense metrics for detected exploits and honeytoken triggers.
- Create honeytokens with `HT-` prefixes and track trigger counts.
- Provide rabbit-hole containment sessions with engage, release, status, response, and async stall operations.
- Apply request processing in this order: containment, blocklist, rate limit, custom rules, cognitive exploit detection.
- Auto-block future requests from sources that trigger critical threats.
- Expose MCP tools for exploit detection, request processing, and threat reports.

## Non-Functional Requirements

- The module is in-process and deterministic except for honeytoken identifiers and generated poison phrase selection.
- Tests must use real instances; no mocks are required for the public contract.
- The compatibility import paths must remain stable for demos and `security.ai_safety`.

## Validation

```bash
uv run pytest tests/unit/defense/ -q
uv run ruff check src/codomyrmex/defense
uv run ty check --output-format concise src/codomyrmex/defense
```

## Navigation

- **README**: [README.md](README.md)
- **Agent Guidance**: [AGENTS.md](AGENTS.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
