# Encryption Module - MCP Tool Specification

**Version**: v0.1.0 | **Status**: Not Applicable | **Last Updated**: February 2026

## Overview

The encryption module intentionally does **not** expose any MCP (Model Context Protocol) tools. Encryption operations involve sensitive key material and should not be invoked through an AI-facing tool interface for the following reasons:

1. **Key exposure risk**: MCP tool calls may log arguments, exposing keys or plaintext to conversation transcripts.
2. **No ambient authority**: Encryption keys should be managed by application code, not passed through an LLM tool call boundary.
3. **Side-effect sensitivity**: File encryption/decryption and key storage have irreversible side effects that require explicit application-level authorization.

## Recommended Usage

Use this module's Python API directly from application code or scripts:

```python
from codomyrmex.encryption import AESGCMEncryptor, generate_aes_key

key = generate_aes_key()
encryptor = AESGCMEncryptor(key)
ciphertext = encryptor.encrypt(b"sensitive data")
```

## Future Considerations

If MCP tool exposure is needed in the future, consider:

- A `hash_data` tool (read-only, no key material) could be safely exposed.
- Any tool involving keys would need a key-reference system (key IDs rather than raw bytes).
- All tool calls should avoid logging plaintext or key material.

## Navigation

- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Module README**: [README.md](README.md)
