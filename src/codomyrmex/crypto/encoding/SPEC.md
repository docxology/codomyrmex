# Crypto Encoding -- Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Encoding and decoding utilities for cryptographic data formats: Base64, Base58, Base32, hexadecimal, and PEM. All functions are pure transformations with no side effects.

## Architecture

```
crypto/encoding/
├── __init__.py   # 12 re-exports across 3 submodules
├── base.py       # Base64, Base58, Base32 encode/decode
├── hex.py        # Hex encode/decode, validation
└── pem.py        # PEM encode/decode, type identification
```

## Key Functions

### base.py

| Name | Signature | Description |
|------|-----------|-------------|
| `encode_base64` | `(data: bytes) -> str` | Encode bytes to Base64 string |
| `decode_base64` | `(data: str) -> bytes` | Decode Base64 string to bytes |
| `encode_base58` | `(data: bytes) -> str` | Encode bytes to Base58 (Bitcoin alphabet) |
| `decode_base58` | `(data: str) -> bytes` | Decode Base58 string to bytes |
| `encode_base32` | `(data: bytes) -> str` | Encode bytes to Base32 string |
| `decode_base32` | `(data: str) -> bytes` | Decode Base32 string to bytes |

### hex.py

| Name | Signature | Description |
|------|-----------|-------------|
| `encode_hex` | `(data: bytes) -> str` | Encode bytes to lowercase hex string |
| `decode_hex` | `(data: str) -> bytes` | Decode hex string to bytes |
| `is_valid_hex` | `(data: str) -> bool` | Check whether a string is valid hexadecimal |

### pem.py

| Name | Signature | Description |
|------|-----------|-------------|
| `encode_pem` | `(data: bytes, label: str) -> str` | Wrap DER bytes in PEM armor with the given label |
| `decode_pem` | `(data: str) -> bytes` | Strip PEM armor and return DER bytes |
| `identify_pem_type` | `(data: str) -> str` | Identify the PEM block type (e.g., "RSA PRIVATE KEY") |

## Dependencies

- Python `base64`, `binascii` (standard library only)

## Constraints

- `decode_base58` raises `ValueError` on invalid characters (not in Bitcoin Base58 alphabet).
- `decode_pem` expects well-formed `-----BEGIN ... -----` / `-----END ... -----` delimiters.
- All encode functions return `str`; all decode functions return `bytes`.

## Error Handling

| Error | When |
|-------|------|
| `ValueError` | Invalid encoding input (bad Base58 chars, malformed PEM, odd-length hex) |
| `binascii.Error` | Corrupt Base64/Base32 padding |

## Navigation

- **Parent**: [crypto/SPEC.md](../SPEC.md)
- **Siblings**: [AGENTS.md](AGENTS.md), [README.md](README.md), [PAI.md](PAI.md)
