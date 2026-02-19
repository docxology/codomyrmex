# Encryption Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Encryption module for Codomyrmex.

## Key Features

- `encrypt()` — Encrypt data.
- `decrypt()` — Decrypt data.
- `generate_key()` — Generate an encryption key.
- `get_encryptor()` — Get an encryptor instance.

## Quick Start

```python
from codomyrmex.encryption import encrypt, decrypt, generate_key

# Use the module
result = encrypt()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Functions

| Function | Description |
|----------|-------------|
| `encrypt()` | Encrypt data. |
| `decrypt()` | Decrypt data. |
| `generate_key()` | Generate an encryption key. |
| `get_encryptor()` | Get an encryptor instance. |
| `encrypt_file()` | Encrypt a file. |
| `decrypt_file()` | Decrypt a file. |
| `hash_data()` | Compute hash of data. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |



## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k encryption -v
```

## Related Modules

- [Exceptions](../exceptions/README.md)

## Navigation

- **Source**: [src/codomyrmex/encryption/](../../../src/codomyrmex/encryption/)
- **Parent**: [Modules](../README.md)
