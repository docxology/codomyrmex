# Governance Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Legal and policy framework for decentralized agent operations. Handles contract generation, policy-as-code enforcement, and dispute resolution.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **`Contract`** -- Smart and legal contract wrapper.
- **`Policy`** -- Executable governance rule for enforcement.
- **`Arbitrator`** -- Dispute resolution engine.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `contracts` | Agreements and terms |
| `policy` | Rule enforcement |
| `dispute_resolution` | Arbitration logic |

## Quick Start

```python
from codomyrmex.governance import Contract, Policy

policy = Policy(rule="No spending > $500 without approval")
policy.enforce(transaction)
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Contract` | Smart and legal contract wrapper |
| `Policy` | Executable governance rule |
| `Arbitrator` | Dispute resolution engine |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k governance -v
```

## Related Modules

- [Finance](../finance/README.md)
- [Smart Contracts](../smart_contracts/README.md)

## Navigation

- **Source**: [src/codomyrmex/governance/](../../../src/codomyrmex/governance/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/governance/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/governance/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
