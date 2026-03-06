# Crypto Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Comprehensive cryptographic operations including symmetric/asymmetric encryption, hashing, digital signatures, KDF, certificates, cryptocurrency, cryptanalysis, steganography, and encoding.

## Configuration Options

The crypto module operates with sensible defaults and does not require environment variable configuration. Cryptographic parameters (key sizes, algorithms) are set per-operation. No global configuration required. Uses Python cryptography library.

## MCP Tools

This module exposes 3 MCP tool(s):

- `hash_data`
- `verify_hash`
- `generate_key`

## PAI Integration

PAI agents invoke crypto tools through the MCP bridge. Cryptographic parameters (key sizes, algorithms) are set per-operation. No global configuration required. Uses Python cryptography library.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep crypto

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/crypto/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
