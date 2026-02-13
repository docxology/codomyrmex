# Personal AI Infrastructure -- Governance Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Governance module provides the **legal and policy framework** for decentralized agent operations in the Codomyrmex ecosystem. It handles contract lifecycle management (draft, sign, activate, terminate), policy-as-code enforcement with composable rule engines, and compliance visualization.

## PAI Capabilities

### Contract Management

Create, sign, and manage contracts between agents:

```python
from codomyrmex.governance.contracts import Contract, Party

parties = [
    Party(id="agent-1", name="Builder Agent", role="contractor"),
    Party(id="agent-2", name="QA Agent", role="reviewer"),
]
contract = Contract(title="Code Review Agreement", text="...", parties=parties)
contract.sign("agent-1")
contract.sign("agent-2")  # Auto-activates when all parties sign
print(contract.status)     # ContractStatus.ACTIVE
```

### Policy-as-Code Enforcement

Define and enforce executable governance rules:

```python
from codomyrmex.governance.policy import Policy, PolicyEngine

engine = PolicyEngine()
engine.add_policy(Policy(
    name="budget-cap",
    rule=lambda ctx: ctx.get("amount", 0) <= 500,
    error_message="Spending exceeds $500 limit"
))
engine.enforce({"amount": 100})    # Passes
engine.enforce({"amount": 1000})   # Raises PolicyError
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Contract` | Class | Legal/smart contract with signing lifecycle and auto-activation |
| `Party` | Dataclass | Contract party with id, name, and role |
| `Signature` | Dataclass | Digital signature record with signer ID and timestamp |
| `ContractStatus` | Enum | Lifecycle states: DRAFT, ACTIVE, TERMINATED, DISPUTED |
| `Policy` | Class | Executable governance rule with callable validation |
| `PolicyEngine` | Class | Composable engine that enforces multiple policies against a context |
| `PolicyError` | Exception | Raised when policy rules are violated |

## PAI Algorithm Phase Mapping

| Phase | Governance Module Contribution |
|-------|-------------------------------|
| **OBSERVE** | Contract status and policy compliance data provide governance observability |
| **PLAN** | Policy rules define constraints that must be satisfied during planning |
| **EXECUTE** | `PolicyEngine.enforce()` validates actions before execution proceeds |
| **VERIFY** | Contract signing validation and policy checks enforce correctness at the verification boundary |
| **LEARN** | Policy violation history informs governance rule refinement |

## Architecture Role

**Application Layer** -- Domain-specific governance and compliance module. Depends on the `visualization` module for compliance charting. Has no upward dependencies from other modules.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
