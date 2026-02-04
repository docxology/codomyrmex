# Codomyrmex Agents - docs/modules/wallet

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Documentation files and guides for the `wallet` module. Provides secure self-custody key management, message signing, Natural Ritual recovery, encrypted backups, and policy-driven key rotation for cognitive agents.

## Active Components

- `README.md` - Module documentation with architecture overview and quick start
- `SPEC.md` - Functional specification (points to authoritative source spec)

## Source Documentation

The following documentation files are maintained alongside the source code:

| File | Description |
|------|-------------|
| `API_SPECIFICATION.md` | Complete API reference for all classes and methods |
| `MCP_TOOL_SPECIFICATION.md` | Model Context Protocol tool definitions |
| `SECURITY.md` | Security policy, threat model, and best practices |
| `USAGE_EXAMPLES.md` | Practical usage examples with expected outcomes |
| `CHANGELOG.md` | Version history with Keep a Changelog format |
| `AGENTS.md` | Agent-specific usage guide and operating contracts |

## Module Exports

```python
# Classes
WalletManager, NaturalRitualRecovery, BackupManager, KeyRotation, Wallet
RitualStep, RotationRecord, RotationPolicy

# Exceptions
WalletError, WalletNotFoundError, WalletKeyError, RitualError

# Functions
hash_response, create_wallet, get_wallet_manager
```

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Keys are never logged, exported, or included in backup plaintext.

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [modules](../README.md) - Parent directory documentation
- **Project Root**: [README](../../../README.md) - Main project documentation
