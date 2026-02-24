# crypto/encoding -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `crypto/encoding` submodule provides encoding and decoding utilities commonly used in cryptographic workflows: Base64, Base58, Base32, hexadecimal, and PEM format operations.

## When to Use This Module

- You need to encode binary data (keys, ciphertext, hashes) for text-safe transport or storage
- You need Base58 encoding for cryptocurrency addresses or identifiers
- You need to encode/decode PEM-formatted certificates, keys, or CSRs
- You need to validate whether a string is valid hexadecimal
- You need to identify the type of data inside a PEM block (certificate, private key, etc.)

## Exports

| Name | Kind | Purpose |
|------|------|---------|
| `encode_base64` / `decode_base64` | function | Standard Base64 encode/decode |
| `encode_base58` / `decode_base58` | function | Base58 encode/decode (Bitcoin-style) |
| `encode_base32` / `decode_base32` | function | Base32 encode/decode |
| `encode_hex` / `decode_hex` | function | Hex string encode/decode |
| `is_valid_hex` | function | Validate hex string format |
| `encode_pem` / `decode_pem` | function | PEM envelope encode/decode |
| `identify_pem_type` | function | Detect PEM block type (CERTIFICATE, PRIVATE KEY, etc.) |

## Example Agent Usage

```python
from codomyrmex.crypto.encoding import (
    encode_base64, decode_base64, encode_hex, is_valid_hex, identify_pem_type,
)

# Base64 round-trip
encoded = encode_base64(b"\x00\xff\x10")
original = decode_base64(encoded)

# Hex validation
assert is_valid_hex("deadbeef")
assert not is_valid_hex("not-hex")

# PEM type detection
pem_data = b"-----BEGIN CERTIFICATE-----\n..."
pem_type = identify_pem_type(pem_data)  # "CERTIFICATE"
```

## Constraints

- All encode functions accept `bytes`; decode functions return `bytes`.
- `encode_base58` / `decode_base58` use the Bitcoin alphabet (no 0, O, I, l).
- `identify_pem_type` parses the PEM header; does not validate the enclosed data.

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `crypto.graphy` | Keys and certs produced by `graphy` often need PEM/hex/base64 encoding |
| `crypto.currency` | Bitcoin addresses use Base58 encoding |
| `encryption.core` | `Encryptor.encrypt_string()` uses Base64 internally |
