# Finance Agents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Specialized agents for financial operations.

## Agents

### `AccountantAgent` (Ledger)

- **Role**: Maintains the books, reconciles accounts.
- **Capabilities**: `read_ledger`, `post_transaction`, `reconcile`.

### `CFOAgent` (Forecasting)

- **Role**: Strategic financial planning.
- **Capabilities**: `analyze_burn_rate`, `allocate_budget`, `audit_spending`.

### `ComplianceAgent` (Taxes)

- **Role**: Ensures regulatory adherence.
- **Capabilities**: `calculate_tax`, `generate_reports`.

## Tools

| Tool | Agent | Description |
| :--- | :--- | :--- |
| `post_entry` | Accountant | Record a transaction |
| `run_forecast` | CFO | Generate cashflow projection |
| `audit_log` | Compliance | Review financial history |

## Integration

These agents integrate with `codomyrmex.agents.core` and use the MCP protocol for tool access.

## Navigation

- [README](README.md) | [SPEC](SPEC.md)
