# Encryption Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Encryption, hashing, digital signatures, and key management. Provides AES-256 (CBC/GCM), RSA, PBKDF2, HKDF, HMAC, and secure data containers. This specification documents the configuration schema and constraints.

## Configuration Schema

The encryption module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Encryption keys are managed through KeyManager. Key derivation parameters (iterations, salt length) are configurable per-operation. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Encryption keys are managed through KeyManager. Key derivation parameters (iterations, salt length) are configurable per-operation.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/encryption/SPEC.md)
