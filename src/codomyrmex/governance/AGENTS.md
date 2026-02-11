# Governance Agents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Agents responsible for legal drafting, compliance checking, and arbitration.

## Agents

### `LegalAgent` (Contracts)

- **Role**: Drafts and reviews contracts.
- **Capabilities**: `draft_contract`, `review_terms`.

### `ComplianceOfficer` (Policy)

- **Role**: Enforces real-time policy adherence.
- **Capabilities**: `audit_action`, `block_violation`.

### `ArbiterAgent` (Dispute Resolution)

- **Role**: Resolves conflicts between agents.
- **Capabilities**: `mediate_dispute`, `issue_ruling`.

## Tools

| Tool | Agent | Description |
| :--- | :--- | :--- |
| `validate_contract` | LegalAgent | Check contract validity |
| `policy_check` | ComplianceOfficer | Verify action against policy |

## Integration

These agents integrate with `codomyrmex.agents.core` and use the MCP protocol for tool access.

## Navigation

- [README](README.md) | [SPEC](SPEC.md)
