# Encryption

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Encryption module for Codomyrmex.

## Architecture Overview

```
encryption/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`Encryptor`**
- **`KeyManager`**
- **`AESGCMEncryptor`**
- **`SecureDataContainer`**
- **`EncryptionError`**
- **`Signer`**
- **`encrypt`**
- **`decrypt`**
- **`generate_key`**
- **`get_encryptor`**
- **`encrypt_data`**
- **`decrypt_data`**
- **`generate_aes_key`**
- **`encrypt_file`**
- **`decrypt_file`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `encryption_encrypt` | Safe |
| `encryption_generate_key` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/encryption/](../../../../src/codomyrmex/encryption/)
- **Parent**: [All Modules](../README.md)
