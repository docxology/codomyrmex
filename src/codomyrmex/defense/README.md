# defense

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The defense module provides active countermeasures against cognitive exploits such as prompt injections and jailbreak attempts. It detects known attack patterns using heuristic scanning, generates adversarial noise to disrupt attacker models, and contains persistent attackers in simulated "rabbit hole" environments that waste their time and resources.

## Key Exports

- **`ActiveDefense`** -- Detects cognitive exploits via pattern matching, generates adversarial "poison" context to disrupt attacker models, and maintains threat metrics. Supports dynamic pattern updates at runtime.
- **`RabbitHole`** -- Simulated containment environment that engages detected attackers in fake interactive sessions, returning nonsensical high-latency responses and supporting async stalling to consume attacker resources.

## Directory Contents

- `__init__.py` - Module entry point; exports `ActiveDefense` and `RabbitHole`
- `active.py` - `ActiveDefense` class with exploit detection, pattern management, poison context generation, and threat reporting
- `rabbithole.py` - `RabbitHole` class with session engagement, decoy response generation, and async stalling
- `defense.py` - Additional defense utilities
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool definitions
- `SPEC.md` - Module specification
- `SECURITY.md` - Security considerations
- `CHANGELOG.md` - Version history
- `USAGE_EXAMPLES.md` - Usage examples and patterns
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/defense/](../../../docs/modules/defense/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
