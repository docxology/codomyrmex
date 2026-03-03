# Crypto -- MCP Tool Specification

This document specifies the MCP-discoverable tools exposed by the `crypto` module. These tools provide cryptographic hashing, hash verification, and key generation capabilities.

## General Considerations

- **Auto-Discovery**: Tools use the `@mcp_tool(category="crypto")` decorator and are auto-discovered via the MCP bridge.
- **Dependencies**: Uses Python standard library modules (`hashlib`, `hmac`, `secrets`, `base64`). No external dependencies.
- **Error Handling**: All tools return `{"status": "error", "message": "..."}` on failure.

---

## Tool: `hash_data`

### 1. Tool Purpose and Description

Compute a cryptographic hash of the input data. Supports multiple hash algorithms and returns the hex digest.

### 2. Invocation Name

`hash_data`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `data` | `string` | Yes | String data to hash | `"Hello, world!"` |
| `algorithm` | `string` | No | Hash algorithm (default: `"sha256"`). One of: `"sha256"`, `"sha384"`, `"sha512"`, `"sha3_256"`, `"blake2b"` | `"sha512"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `algorithm` | `string` | Algorithm used for hashing | `"sha256"` |
| `digest` | `string` | Hex-encoded hash digest | `"315f5bdb76d078c43b8ac0064e4a..."` |
| `digest_length` | `integer` | Length of the hex digest string in characters | `64` |
| `message` | `string` | Error description (only on error) | `"Unsupported algorithm: md5"` |

### 5. Error Handling

- Unsupported algorithm values return an error status before any hashing occurs.
- Encoding or hashing failures return an error with the exception message.

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: The same data and algorithm always produce the same digest. No state is modified.

### 7. Usage Examples

```json
{
  "tool_name": "hash_data",
  "arguments": {
    "data": "my secret document content",
    "algorithm": "sha256"
  }
}
```

### 8. Security Considerations

- Input data is encoded as UTF-8 before hashing. Binary data must be string-encoded by the caller.
- The supported algorithm set excludes weak algorithms (MD5, SHA-1) by design.
- Hash digests are not secret, but the input data may be. Callers should avoid logging sensitive inputs.

---

## Tool: `verify_hash`

### 1. Tool Purpose and Description

Verify that data matches an expected hash. Uses constant-time comparison (`hmac.compare_digest`) to prevent timing attacks.

### 2. Invocation Name

`verify_hash`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `data` | `string` | Yes | String data to verify | `"Hello, world!"` |
| `expected_hash` | `string` | Yes | Expected hex digest to compare against | `"315f5bdb76d078c43b8ac0064e4a..."` |
| `algorithm` | `string` | No | Hash algorithm used for the expected hash (default: `"sha256"`) | `"sha256"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `match` | `boolean` | Whether the computed hash matches the expected hash | `true` |
| `algorithm` | `string` | Algorithm used for verification | `"sha256"` |
| `message` | `string` | Error description (only on error) | `"new() missing required argument"` |

### 5. Error Handling

- Invalid algorithm names cause a hashing exception, returned as an error status.
- Malformed expected_hash values will result in `match: false` (not an error), since the comparison is purely string-based.

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Verification is a pure read operation. The same inputs always produce the same match result.

### 7. Usage Examples

```json
{
  "tool_name": "verify_hash",
  "arguments": {
    "data": "my secret document content",
    "expected_hash": "a1b2c3d4e5f6...",
    "algorithm": "sha256"
  }
}
```

### 8. Security Considerations

- Uses `hmac.compare_digest` for constant-time comparison, preventing timing-based side-channel attacks.
- The `expected_hash` parameter may reveal information about the original data; handle with care.

---

## Tool: `generate_key`

### 1. Tool Purpose and Description

Generate a cryptographic key using a cryptographically secure random number generator (`secrets.token_bytes`). Supports AES and HMAC key types with hex or base64 encoding.

### 2. Invocation Name

`generate_key`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `algorithm` | `string` | No | Key type (default: `"aes256"`). One of: `"aes128"` (16 bytes), `"aes256"` (32 bytes), `"hmac256"` (32 bytes) | `"aes128"` |
| `encoding` | `string` | No | Output encoding (default: `"hex"`). One of: `"hex"`, `"base64"` | `"base64"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `algorithm` | `string` | Key type generated | `"aes256"` |
| `encoding` | `string` | Encoding of the key string | `"hex"` |
| `key` | `string` | The generated key material | `"a3f1b2c4d5e6..."` |
| `key_bits` | `integer` | Key size in bits | `256` |
| `message` | `string` | Error description (only on error) | `"Unsupported algorithm: rsa2048"` |

### 5. Error Handling

- Unsupported algorithm values return an error status before any key generation occurs.
- Unexpected encoding failures return an error with the exception message.

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Each call generates a new random key. Repeated calls with the same parameters produce different keys.

### 7. Usage Examples

```json
{
  "tool_name": "generate_key",
  "arguments": {
    "algorithm": "aes256",
    "encoding": "base64"
  }
}
```

### 8. Security Considerations

- Generated keys use `secrets.token_bytes`, which is cryptographically secure.
- Key material is returned in the response. Callers must store keys securely and avoid logging them.
- This tool generates symmetric keys only. It does not support asymmetric key generation.

---

## Navigation Links

- **Parent**: [Module README](./README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Home**: [Root README](../../../README.md)
