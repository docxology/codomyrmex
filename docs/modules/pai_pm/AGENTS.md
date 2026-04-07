# Pai Pm Module — Agent Coordination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `docs/modules/pai_pm`
- **Human overview**: [README.md](README.md)
- **Functional spec**: [SPEC.md](SPEC.md)
- **Agent coordination** (repo root): [../../../AGENTS.md](../../../AGENTS.md)

## Purpose

Codomyrmex pai_pm module — PAI Project Manager server wrapper.

## Key Capabilities

- Pai Pm operations and management

## Agent Usage Patterns

```python
from codomyrmex.pai_pm import *

# Agent uses pai pm capabilities
```

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Integration Points

- **Source**: [src/codomyrmex/pai_pm/](../../../src/codomyrmex/pai_pm/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
