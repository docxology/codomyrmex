# Contracts -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Smart contract interaction layer providing ABI parsing, transaction construction, event querying, and contract lifecycle management. Supports EVM-compatible networks via the `Network` enum.

## Architecture

```
Contract(name, abi_json)           TransactionBuilder()
  +-- functions: dict                +-- to / value / data / gas_limit / ...
  +-- get_function(name)             +-- validate() -> list[str]
  +-- list_functions()               +-- build() -> Transaction
  +-- view_functions()
  +-- payable_functions()          EventLog()
                                     +-- add(event) / query(filter)
ContractCall(contract, fn_name)      +-- group_by_name / group_by_block
  +-- with_args(**kwargs)            +-- event_frequency / export_json
  +-- with_value(wei)
  +-- encode() -> str              ContractRegistry()
  +-- to_transaction() -> Tx         +-- register / deploy / activate
                                     +-- deprecate / archive / get_history
```

## Key Classes

### Contract Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_function(name)` | `ContractFunction` | Lookup by name; `KeyError` if missing |
| `list_functions()` | `list[str]` | All function names |
| `view_functions()` | `list[ContractFunction]` | Non-mutating functions only |
| `payable_functions()` | `list[ContractFunction]` | Functions accepting ETH |
| `validate()` | `list[str]` | ABI validation errors |

### TransactionBuilder Chain

| Method | Parameter | Description |
|--------|-----------|-------------|
| `.to(address)` | `str` | Recipient address |
| `.value(amount)` | `int` | Wei amount |
| `.data(hex_data)` | `str` | Encoded call data |
| `.gas_limit(limit)` | `int` | Gas limit |
| `.gas_price(price)` | `int` | Gas price in wei |
| `.nonce(n)` | `int` | Transaction nonce |
| `.chain_id(id)` | `int` | Network chain ID |
| `.build()` | -> `Transaction` | Construct final transaction |

### ContractRegistry Lifecycle

| Status | Transitions To | Method |
|--------|---------------|--------|
| `DRAFT` | `DEPLOYED` | `deploy(name, address, network)` |
| `DEPLOYED` | `ACTIVE` | `activate(name)` |
| `ACTIVE` | `DEPRECATED` | `deprecate(name, reason)` |
| `DEPRECATED` | `ARCHIVED` | `archive(name)` |

### Address Validation

- EVM networks: must start with `0x` and be exactly 42 characters.
- Solana: length validation only (32-44 base58 characters).

## Dependencies

- `hashlib` (stdlib) for SHA3-256 function selectors
- `uuid`, `datetime`, `json`, `enum` (stdlib)

## Constraints

- ABI parsing is JSON-based; binary ABI formats are not supported.
- Gas estimation uses simplified heuristic (base 21000 + 68 per non-zero byte).
- Event storage is in-memory; no persistence across process restarts.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [wallet](../README.md)
