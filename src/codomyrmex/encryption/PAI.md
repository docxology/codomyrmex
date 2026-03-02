# Personal AI Infrastructure — Encryption Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Encryption module provides symmetric and asymmetric encryption, key generation, and secure data handling for protecting sensitive information in AI agent workflows. It ensures data-at-rest and data-in-transit security.

## PAI Capabilities

### Encryption Operations

- Symmetric encryption (AES-256-GCM)
- Asymmetric encryption (RSA, Ed25519)
- Key pair generation and management
- Secure envelope encryption for large payloads
- Password-based key derivation (Argon2)

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| Symmetric engines | Various | AES-based encryption/decryption |
| Asymmetric engines | Various | RSA/Ed25519 key operations |
| Key generators | Various | Cryptographic key generation |

## PAI Algorithm Phase Mapping

| Phase | Encryption Contribution |
|-------|--------------------------|
| **BUILD** | Encrypt sensitive artifacts before storage |
| **EXECUTE** | Secure data transfer between agents and services |
| **VERIFY** | Verify data integrity via encryption-based checksums |

## Architecture Role

**Core Layer** — Foundational cryptography consumed by `wallet/`, `auth/`, `security/`, and `privacy/` modules.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.encryption import ...`
- CLI: `codomyrmex encryption <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
