# Governance Module — Agent Coordination

## Purpose

Governance Module for Codomyrmex.

Provides contracts management, policy enforcement, and dispute resolution.

Submodules:
    contracts -- Contract lifecycle management with terms, signing, and compliance
    policy -- Rule-based policy engine with evaluation and enforcement
    dispute_resolution -- Dispute filing, evidence, mediation, and resolution workflow

## Key Capabilities

- **`Contract`** — Smart and legal contract wrapper
- **`Policy`** — Executable governance rule
- **`Arbitrator`** — Dispute resolution engine
- `contracts/` — Agreements and terms
- `policy/` — Rule enforcement
- `dispute_resolution/` — Arbitration logic

## Agent Usage Patterns

```python
from codomyrmex.governance import Contract, Policy

policy = Policy(rule="No spending > $500 without approval")
policy.enforce(transaction)
```

## Key Components

| Export | Type |
|--------|------|
| `Contract` | Public API |
| `ContractTerm` | Public API |
| `ContractStatus` | Public API |
| `ContractError` | Public API |
| `PolicyRule` | Public API |
| `PolicyEngine` | Public API |
| `PolicyError` | Public API |
| `DisputeResolver` | Public API |
| `DisputeStatus` | Public API |
| `DisputeError` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `contracts.py` | Represents a legal or smart contract between agents. |
| `policy.py` | Exception raised when a policy violation occurs. |
| `visualization.py` | Renders a pie chart of policy compliance (pass vs fail). |

## Submodules

- `contracts/` — Contracts
- `dispute_resolution/` — Dispute Resolution
- `policy/` — Policy

## Integration Points

- **Source**: [src/codomyrmex/governance/](../../../src/codomyrmex/governance/)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k governance -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting
