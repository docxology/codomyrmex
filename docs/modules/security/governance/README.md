# Security Governance Submodule

**Version**: v0.1.0 | **Source**: [`src/codomyrmex/security/governance/`](../../../../src/codomyrmex/security/governance/)

## Overview

Governance capabilities including contract lifecycle management, rule-based policy enforcement, dispute resolution workflows, and compliance visualization. Provides the trust and accountability infrastructure for secure operations.

## Components

| Source File | Classes / Functions | Availability Flag |
|-------------|--------------------|--------------------|
| `contracts.py` | `Contract`, `ContractTerm`, `ContractStatus`, `ContractError` | Always available |
| `policy.py` | `PolicyRule`, `PolicyEngine`, `PolicyError` | Always available |
| `dispute_resolution.py` | `DisputeResolver`, `DisputeStatus`, `DisputeError` | Always available |
| `visualization.py` | `plot_policy_compliance()` | Always available |

## Exports (via `governance/__init__.py`)

All 9 symbols are directly exported:
- `Contract`, `ContractTerm`, `ContractStatus`, `ContractError`
- `PolicyRule`, `PolicyEngine`, `PolicyError`
- `DisputeResolver`, `DisputeStatus`, `DisputeError`

## Convenience Functions

| Function | Description |
|----------|-------------|
| `Contract.sign()` | Sign a contract, transitioning to active status |
| `Contract.terminate()` | Terminate an active contract |
| `PolicyEngine.evaluate()` | Evaluate context against all registered rules |
| `PolicyEngine.enforce()` | Evaluate and apply enforcement actions |
| `DisputeResolver.file_dispute()` | File a new dispute |
| `DisputeResolver.resolve()` | Resolve an open dispute |

## Navigation

- **Parent**: [Security Module](../README.md)
- **Source**: [`src/codomyrmex/security/governance/`](../../../../src/codomyrmex/security/governance/)
- **Conceptual Guide**: [Trust and Governance Concepts](../../../security/trust-and-governance.md)
