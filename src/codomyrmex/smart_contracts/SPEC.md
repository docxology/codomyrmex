# Smart Contracts - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Smart contracts module providing blockchain interaction capabilities for Ethereum and other EVM-compatible networks.

## Functional Requirements

- Contract deployment and interaction
- Transaction building and signing
- Gas estimation and management
- Multi-network support (mainnet, testnets)
- ABI encoding/decoding

## Core Classes

| Class | Description |
|-------|-------------|
| `Contract` | Smart contract interface |
| `Transaction` | Transaction representation |
| `TransactionBuilder` | Fluent transaction builder |
| `Network` | Network enum (ETHEREUM, POLYGON, ARBITRUM, OPTIMISM, BASE, SOLANA) |
| `ContractCall` | Fluent contract method call builder |
| `ContractRegistry` | In-memory named contract registry |
| `ContractEvent` | Smart contract event record |
| `EventFilter` | Fluent event filter builder |
| `EventLog` | Event collection and query |

## Key Functions

| Function | Description |
|----------|-------------|
| `wei_to_ether(wei)` | Convert wei to ether |
| `ether_to_wei(ether)` | Convert ether to wei |
| `gwei_to_wei(gwei)` | Convert gwei to wei |

## Supported Networks

- Ethereum, Polygon, Arbitrum, Optimism, Base
- Solana

## Design Principles

1. **Security First**: Safe transaction handling
2. **Gas Efficiency**: Optimal gas estimation
3. **Multi-Chain**: Abstract network differences
4. **Type Safety**: Strong typing for contract calls

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)

## API Usage

```python
from codomyrmex.smart_contracts import Network, TransactionStatus, Address
```
