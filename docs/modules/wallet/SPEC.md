# wallet - Functional Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The `wallet` module provides secure self-custody key management and Natural Ritual recovery for cognitive agents. It enables autonomous agents to hold, sign with, rotate, and recover cryptographic keys without exposing them to external systems.

## Source Specification

The authoritative functional specification is located in the source module:
[src/codomyrmex/wallet/SPEC.md](../../../src/codomyrmex/wallet/SPEC.md)

## Summary

### Core Capabilities

1. **Wallet Creation** - Generate wallet IDs and securely store private keys
2. **Message Signing** - HMAC-SHA256 signing with constant-time verification
3. **Key Rotation** - Policy-driven rotation with audit trail
4. **Backup Management** - Encrypted backup creation and verification
5. **Natural Ritual Recovery** - Multi-step knowledge-based recovery with lockout protection
6. **Wallet Deletion** - Secure removal of wallet and key material

### Components

| Component | Description |
|-----------|-------------|
| `WalletManager` | Core wallet lifecycle and signing |
| `NaturalRitualRecovery` | Knowledge-based recovery |
| `BackupManager` | Encrypted backup management |
| `KeyRotation` | Policy-driven rotation and audit trail |
| `Wallet` | Unified facade |

### Exception Hierarchy

```
CodomyrmexError
  -> WalletError
       -> WalletNotFoundError
       -> WalletKeyError
       -> RitualError
```

### Dependencies

- `codomyrmex.encryption.key_manager.KeyManager`
- `codomyrmex.logging_monitoring.logger_config`

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [modules](../README.md)
- **Project Root**: [README](../../../README.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k wallet -v
```
