# Codomyrmex Agents -- src/codomyrmex/wallet/contracts

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides smart contract modeling, transaction building, event logging, and a versioned contract registry with lifecycle management for blockchain wallet operations.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `Address`, `Transaction`, `ContractFunction` | Core data models for blockchain addresses (with network validation), transactions, and ABI-parsed contract functions |
| `models.py` | `Network`, `TransactionStatus` | Enums for supported blockchain networks (Ethereum, Polygon, Arbitrum, etc.) and transaction lifecycle states |
| `contract.py` | `Contract` | Represents a smart contract with ABI-parsed functions; provides `view_functions`, `payable_functions`, and `validate` |
| `contract.py` | `ContractCall` | Fluent builder for constructing contract function calls with arguments, value, and gas limit; encodes to `Transaction` |
| `builders.py` | `TransactionBuilder` | Fluent API for constructing transactions with validation, auto-gas estimation, and chain ID support |
| `builders.py` | `estimate_gas` / `build_batch` | Gas estimation from calldata bytes and batch transaction creation from transfer specs |
| `events.py` | `ContractEvent`, `EventFilter`, `EventLog` | Event dataclass, fluent query builder for filtering events by name/block/args, and event store with aggregation and export |
| `registry.py` | `ContractRegistry` | Named contract storage with versioning, lifecycle management (DRAFT to ARCHIVED), and tag/status-based filtering |
| `registry.py` | `ContractVersion`, `ContractStatus` | Version snapshot dataclass and lifecycle status enum |

## Operating Contracts

- `Address.is_valid` checks EVM-compatible addresses for `0x` prefix and 42-character length; Solana addresses only require non-empty values.
- `TransactionBuilder.validate` enforces minimum gas limit of 21,000, non-negative values and nonces, and requires data for contract creation (no `to` address).
- `ContractRegistry` enforces lifecycle transitions: DRAFT to DEPLOYED to ACTIVE to DEPRECATED to ARCHIVED; invalid transitions return `False`.
- `EventFilter.matches` applies all criteria as an AND conjunction -- all set filters must pass for a match.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Python standard library (`hashlib`, `dataclasses`, `enum`); no external blockchain SDKs
- **Used by**: `wallet/security` (key management references wallet IDs), wallet CLI commands

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
