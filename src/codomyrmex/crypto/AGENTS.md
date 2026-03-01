# Crypto Module — Agent Capabilities

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Agent Access Matrix

This document defines which PAI agent types can access which crypto submodules and at what trust level.

### Engineer Agent

**Access**: Full access to all submodules
**Trust Level**: TRUSTED

| Submodule | Capabilities |
|---|---|
| graphy/ | Generate keys, encrypt/decrypt, sign/verify, derive keys, manage certificates |
| currency/ | Generate wallets, construct transactions, derive addresses |
| encoding/ | Encode/decode all formats |
| protocols/ | Execute key exchanges, split/reconstruct secrets |
| random/ | Generate cryptographic random values |
| analysis/ | Assess strength, analyze entropy |
| steganography/ | Embed and extract hidden data |

**Use Cases**: Implementing cryptographic features, building secure communication channels, key management infrastructure.

### Architect Agent

**Access**: Read-only analysis, protocol design
**Trust Level**: OBSERVED

| Submodule | Capabilities |
|---|---|
| analysis/ | Full access: entropy, frequency, strength, cipher analysis |
| protocols/ | Read specifications, no key generation |
| graphy/ | Query algorithm availability, no key operations |
| encoding/ | Format validation only |

**Use Cases**: Security architecture review, algorithm selection, protocol design evaluation, threat modeling.

### QATester Agent

**Access**: Validation and verification operations
**Trust Level**: OBSERVED

| Submodule | Capabilities |
|---|---|
| analysis/ | Full access: verify entropy, strength, randomness |
| random/ | Run NIST tests on provided data, no key generation |
| encoding/ | Encode/decode for test data preparation |
| graphy/ | Verify operations (verify_hash, verify_ecdsa, etc.) |
| steganography/ | Detection methods only |

**Use Cases**: Cryptographic correctness testing, randomness quality validation, encoding round-trip verification.

### Security Agent

**Access**: Full access to all submodules
**Trust Level**: TRUSTED

| Submodule | Capabilities |
|---|---|
| All | Full access for security assessment |

**Use Cases**: Penetration testing, security auditing, vulnerability assessment, compliance verification.

## Trust Level Definitions

| Level | Description | Operations Permitted |
|---|---|---|
| UNTRUSTED | No crypto access | None |
| OBSERVED | Read-only, analysis | Hashing, analysis, encoding, verification |
| TRUSTED | Full access | Key generation, encryption, signing, wallet creation |

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Key Parameters | Trust Level |
|------|-------------|----------------|-------------|
| `hash_data` | Compute a cryptographic hash of the input data | `data`, `algorithm` (sha256/sha384/sha512/sha3_256/blake2b) | Safe |
| `verify_hash` | Verify that data matches an expected hash (constant-time comparison) | `data`, `expected_hash`, `algorithm` | Safe |
| `generate_key` | Generate a cryptographic key | `algorithm` (aes128/aes256/hmac256), `encoding` (hex/base64) | Safe |

## CLI Command Access

| Command | Required Trust |
|---|---|
| `crypto:status` | OBSERVED |
| `crypto:algorithms` | OBSERVED |
| `crypto:hash` | OBSERVED |

## Security Constraints

1. **No key export**: Agents at OBSERVED trust level cannot serialize or export private keys.
2. **Audit logging**: All key generation and signing operations are logged via `logging_monitoring`.
3. **Rate limiting**: Key generation operations are rate-limited to prevent resource exhaustion.
4. **No hardcoded secrets**: Agents must never embed generated keys in source code or documentation.
