# Personal AI Infrastructure — Wallet Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Wallet module provides self-custody key management and "Natural Ritual" recovery using zero-knowledge proofs. It enables secure storage of cryptographic keys, API credentials, and agent secrets with recovery mechanisms that don't rely on centralized services. Part of the Secure Cognitive Agent suite.

## PAI Capabilities

### Self-Custody Key Management

```python
from codomyrmex.wallet import Wallet

wallet = Wallet()
# Store and retrieve cryptographic keys
# Self-custody: keys never leave the local system
# Hierarchical key derivation for agent-specific keys
```

### Natural Ritual Recovery (ZKP)

- Recovery without centralized servers using zero-knowledge proofs
- Multi-party threshold recovery for disaster scenarios
- Biometric and cognitive factor integration

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Wallet` | Class | Self-custody key management engine |
| ZKP recovery | Various | Zero-knowledge proof based key recovery |

## PAI Algorithm Phase Mapping

| Phase | Wallet Contribution |
|-------|---------------------|
| **EXECUTE** | Retrieve keys and credentials for secure API access |
| **VERIFY** | Validate key integrity and custody chain |

## Architecture Role

**Specialized Layer** — Part of the Secure Cognitive Agent suite (`identity`, `wallet`, `defense`, `market`, `privacy`). Consumed by `auth/` and `crypto/` for key management.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.wallet import ...`
- CLI: `codomyrmex wallet <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
