# Personal AI Infrastructure — Encryption Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Encryption module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.encryption import Encryptor, KeyManager, AESGCMEncryptor, encrypt, decrypt, generate_key
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Encryptor` | Class | Encryptor |
| `KeyManager` | Class | Keymanager |
| `AESGCMEncryptor` | Class | Aesgcmencryptor |
| `SecureDataContainer` | Class | Securedatacontainer |
| `EncryptionError` | Class | Encryptionerror |
| `encrypt` | Function/Constant | Encrypt |
| `decrypt` | Function/Constant | Decrypt |
| `generate_key` | Function/Constant | Generate key |
| `get_encryptor` | Function/Constant | Get encryptor |
| `encrypt_data` | Function/Constant | Encrypt data |
| `decrypt_data` | Function/Constant | Decrypt data |
| `generate_aes_key` | Function/Constant | Generate aes key |
| `encrypt_file` | Function/Constant | Encrypt file |
| `decrypt_file` | Function/Constant | Decrypt file |
| `hash_data` | Function/Constant | Hash data |

*Plus 4 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Encryption Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **BUILD** | Artifact creation and code generation |
| **VERIFY** | Validation and quality checks |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
