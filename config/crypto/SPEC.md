# Crypto Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Comprehensive cryptographic operations including symmetric/asymmetric encryption, hashing, digital signatures, KDF, certificates, cryptocurrency, cryptanalysis, steganography, and encoding. This specification documents the configuration schema and constraints.

## Configuration Schema

The crypto module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Cryptographic parameters (key sizes, algorithms) are set per-operation. No global configuration required. Uses Python cryptography library. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Cryptographic parameters (key sizes, algorithms) are set per-operation. No global configuration required. Uses Python cryptography library.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/crypto/SPEC.md)
