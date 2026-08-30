<!-- readme: generated -->

# wallet

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/wallet/`

## Overview

Wallet Module.

Provides Secure Self-Custody and Natural Ritual Recovery for cognitive agents.

Core Components:
    WalletManager: Wallet creation, signing, rotation, and lifecycle management.
    NaturalRitualRecovery: Multi-factor knowledge-based key recovery.
    BackupManager: Encrypted backup creation and verification.
    KeyRotation: Policy-driven key rotation with audit trail.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `contracts:` | Consolidated contracts capabilities. |

## Public Exports

`wallet` exports 24 public symbols via `__all__`:

`BackupManager`, `CapabilityAttestation`, `KeyRotation`, `NaturalRitualRecovery`, `RitualError`, `RitualStep`, `RotationPolicy`, `RotationRecord`, `SignedCapabilityProof`, `SignedCapabilityProofBuilder`, `WalletError`, `WalletKeyError`, `WalletManager`, `WalletNotFoundError`, `ZKProof`, `ZKProofVerifier`, `cli_commands`, `contracts`, `create_wallet`, `generate_zk_proof`, `get_wallet_manager`, `hash_response`, `security`, `verify_zk_proof`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../wallet/](../../../../wallet/)
