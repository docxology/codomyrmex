# Encryption Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Encryption, hashing, digital signatures, and key management. Provides AES-256 (CBC/GCM), RSA, PBKDF2, HKDF, HMAC, and secure data containers.

## Configuration Options

The encryption module operates with sensible defaults and does not require environment variable configuration. Encryption keys are managed through KeyManager. Key derivation parameters (iterations, salt length) are configurable per-operation.

## MCP Tools

This module exposes 2 MCP tool(s):

- `encryption_encrypt`
- `encryption_decrypt`

## PAI Integration

PAI agents invoke encryption tools through the MCP bridge. Encryption keys are managed through KeyManager. Key derivation parameters (iterations, salt length) are configurable per-operation.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep encryption

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/encryption/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
