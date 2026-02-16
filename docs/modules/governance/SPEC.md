# Governance — Functional Specification

**Module**: `codomyrmex.governance`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Governance Module for Codomyrmex.

Provides contracts management, policy enforcement, and dispute resolution.

Submodules:
    contracts -- Contract lifecycle management with terms, signing, and compliance
    policy -- Rule-based policy engine with evaluation and enforcement
    dispute_resolution -- Dispute filing, evidence, mediation, and resolution workflow

## 2. Architecture

### Source Files

| File | Purpose |
|------|--------|
| `contracts.py` | Represents a legal or smart contract between agents. |
| `policy.py` | Exception raised when a policy violation occurs. |
| `visualization.py` | Renders a pie chart of policy compliance (pass vs fail). |

### Submodule Structure

- `contracts/` — Contracts
- `dispute_resolution/` — Dispute Resolution
- `policy/` — Policy

## 3. Dependencies

No internal Codomyrmex dependencies.

## 4. Public API

### Exports (`__all__`)

- `Contract`
- `ContractTerm`
- `ContractStatus`
- `ContractError`
- `PolicyRule`
- `PolicyEngine`
- `PolicyError`
- `DisputeResolver`
- `DisputeStatus`
- `DisputeError`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k governance -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/governance/)
