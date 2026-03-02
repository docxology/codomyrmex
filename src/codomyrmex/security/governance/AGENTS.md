# Codomyrmex Agents — src/codomyrmex/security/governance

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Inter-agent governance providing contract lifecycle management with multi-party signing, rule-based policy enforcement with priority-ordered evaluation, and formal dispute resolution workflows.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `contracts.py` | `ContractStatus` | Enum: `DRAFT`, `ACTIVE`, `EXPIRED`, `TERMINATED`, `DISPUTED` |
| `contracts.py` | `ContractTerm` | Dataclass with `type` validation (obligation/prohibition/permission), `fulfill()`, `is_overdue()` |
| `contracts.py` | `Contract` | Multi-party contract: `add_term()`, `sign()` (auto-activates when all sign), `expire()`, `terminate()`, `dispute()`, `check_compliance()` |
| `contracts.py` | `ContractError` | Exception for invalid operations (e.g., signing non-DRAFT, duplicate parties) |
| `policy.py` | `PolicyRule` | Callable-based rule with `name`, `condition`, `action`, `priority`; `evaluate()` catches exceptions and returns `False` |
| `policy.py` | `PolicyEngine` | Named policy containers: `create_policy()`, `add_rule()`, `evaluate()` (priority-descending), `get_violations()`, `enforce()` |
| `policy.py` | `PolicyError` | Exception for duplicate policies or missing policy names |
| `dispute_resolution.py` | `DisputeStatus` | Enum: `OPEN`, `UNDER_REVIEW`, `RESOLVED`, `CLOSED` |
| `dispute_resolution.py` | `Dispute` | Dataclass with `contract_id`, `filer_id`, `description`, `resolution` |
| `dispute_resolution.py` | `DisputeResolver` | Dispute lifecycle: `file_dispute()`, `resolve_dispute()`, `get_dispute()` |

## Operating Contracts

- `Contract` requires at least 2 unique parties; `ContractError` raised on duplicates or fewer than 2.
- Terms can only be added to `DRAFT` contracts; term `party` must be in the contract's party list.
- `Contract.sign()` auto-transitions to `ACTIVE` when all parties have signed.
- `PolicyEngine.evaluate()` sorts rules by descending `priority` before evaluation.
- `PolicyRule.evaluate()` catches exceptions and returns `False` (logged as warning).
- `DisputeResolver` rejects duplicate dispute IDs via `DisputeError`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library (`uuid`, `logging`, `datetime`)
- **Used by**: Agent collaboration protocols, multi-agent agreements, security policy enforcement

## Navigation

- **Parent**: [security](../README.md)
- **Root**: [Root](../../../../README.md)
