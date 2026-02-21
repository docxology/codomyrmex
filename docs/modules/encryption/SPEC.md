# Encryption — Functional Specification

**Module**: `codomyrmex.encryption`  
**Version**: v1.0.0  
**Status**: Active

## 1. Overview

Encryption module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `encrypt()` | Function | Encrypt data. |
| `decrypt()` | Function | Decrypt data. |
| `generate_key()` | Function | Generate an encryption key. |
| `get_encryptor()` | Function | Get an encryptor instance. |
| `encrypt_file()` | Function | Encrypt a file. |

### Source Files

- `aes_gcm.py`
- `container.py`
- `encryptor.py`
- `hmac_utils.py`
- `kdf.py`
- `key_manager.py`

## 3. Dependencies

See `src/codomyrmex/encryption/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.encryption import encrypt, decrypt, generate_key, get_encryptor, encrypt_file
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k encryption -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/encryption/)
