# Codomyrmex Agents - src/codomyrmex/defense

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Local active-defense compatibility package for prompt-exploit detection,
honeytokens, context poisoning, rate limiting, threat rules, and containment.

## Active Components

- `active.py` - ActiveDefense, ThreatLevel, and RabbitHole primitives.
- `defense.py` - RateLimiter, ThreatDetector, ThreatEvent, DetectionRule, and Defense orchestrator.
- `mcp_tools.py` - MCP wrappers for detection, request processing, and reports.
- `rabbithole.py` - Backward-compatible RabbitHole import path.
- `README.md` - Module overview and quick start.
- `SPEC.md` - Functional and non-functional requirements.
- `API_SPECIFICATION.md` - Public Python API contract.
- `MCP_TOOL_SPECIFICATION.md` - MCP tool contract.

## Operating Contracts

- Preserve legacy imports from `codomyrmex.defense` and `codomyrmex.defense.active`.
- Keep `codomyrmex.security.ai_safety` imports functional.
- Maintain zero-mock tests against real implementations.
- Treat high-risk prompt patterns as containment candidates without claiming external security guarantees.

## Key Files

- `AGENTS.md` - Agent coordination and navigation.
- `README.md` - User-facing module overview.
- `SPEC.md` - Module behavior contract.
- `API_SPECIFICATION.md` - Python API reference.
- `MCP_TOOL_SPECIFICATION.md` - MCP tool reference.
- `active.py`
- `defense.py`
- `mcp_tools.py`
- `rabbithole.py`

## Dependencies

- Uses only Python standard library modules plus the local MCP decorator.

## Development Guidelines

- Keep behavior deterministic and in-process.
- Add or update zero-mock tests when return shapes, threat levels, or response actions change.
- Keep AI-safety facade imports synchronized with public exports.

## Navigation Links

- **Module Overview**: [README.md](README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **Parent Package**: [../README.md](../README.md)
