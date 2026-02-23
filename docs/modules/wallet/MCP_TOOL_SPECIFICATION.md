# Wallet - MCP Tool Specification

## General Considerations for Wallet Tools

- **Dependencies**: All tools require the `encryption` module (for `KeyManager`) and `logging_monitoring` module.
- **Initialization**: `WalletManager` must be instantiated before tool invocation. Key storage directory should be configured.
- **Error Handling**: Errors are logged via `logging_monitoring`. Tools return `{"error": "description"}` on failure.
- **Security**: Private keys are never exposed in tool outputs. Only hashes and metadata are returned.

---

## Tool: `wallet_create`

### 1. Tool Purpose and Description

Creates a new self-custody wallet for a specified user. Generates a wallet address and securely stores the private key via the encryption module's KeyManager.

### 2. Invocation Name

`wallet_create`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description                          | Example Value |
| :------------- | :------- | :------- | :----------------------------------- | :------------ |
| `user_id`      | `string` | Yes      | Unique identifier for wallet owner   | `"agent_001"` |
| `storage_path` | `string` | No       | Key storage directory path           | `"/tmp/keys"` |

### 4. Output Schema (Return Value)

| Field Name       | Type     | Description                    | Example Value                          |
| :--------------- | :------- | :----------------------------- | :------------------------------------- |
| `wallet_address` | `string` | Generated 0x-prefixed address  | `"0x1a2b3c4d5e6f..."` |
| `user_id`        | `string` | Owner user ID                  | `"agent_001"`                          |
| `status`         | `string` | Operation result               | `"success"`                            |

### 5. Error Handling

- `WALLET_EXISTS`: User already has a wallet.
- `KEY_STORAGE_FAILED`: Key could not be persisted.

### 6. Idempotency

- **Idempotent**: No. Each call creates a new wallet. Calling for an existing user raises an error.

### 7. Usage Examples

```json
{
  "tool_name": "wallet_create",
  "arguments": {
    "user_id": "agent_001"
  }
}
```

### 8. Security Considerations

- **Input Validation**: `user_id` is validated as non-empty string.
- **Data Handling**: Private keys are stored with 0o600 permissions. Never returned in output.
- **Permissions**: Requires write access to key storage directory.

---

## Tool: `wallet_sign`

### 1. Tool Purpose and Description

Signs a message using the user's wallet private key via HMAC-SHA256.

### 2. Invocation Name

`wallet_sign`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description                 | Example Value          |
| :------------- | :------- | :------- | :-------------------------- | :--------------------- |
| `user_id`      | `string` | Yes      | Wallet owner user ID        | `"agent_001"`          |
| `message`      | `string` | Yes      | Base64-encoded message      | `"SGVsbG8gV29ybGQ="` |

### 4. Output Schema (Return Value)

| Field Name  | Type     | Description                   | Example Value              |
| :---------- | :------- | :---------------------------- | :------------------------- |
| `signature` | `string` | Base64-encoded HMAC signature | `"a1b2c3d4e5f6..."`     |
| `status`    | `string` | Operation result              | `"success"`                |

### 5. Error Handling

- `WALLET_NOT_FOUND`: No wallet exists for user.
- `KEY_LOCKED`: Key retrieval failed.

### 6. Idempotency

- **Idempotent**: Yes. Same input always produces the same signature.

### 7. Usage Examples

```json
{
  "tool_name": "wallet_sign",
  "arguments": {
    "user_id": "agent_001",
    "message": "SGVsbG8gV29ybGQ="
  }
}
```

### 8. Security Considerations

- **Data Handling**: Private key is used in-memory only, never logged or returned.
- **Output Sanitization**: Only the signature is returned, not the key.

---

## Tool: `wallet_rotate_keys`

### 1. Tool Purpose and Description

Rotates the private key for a user's wallet. Generates new key material and wallet address.

### 2. Invocation Name

`wallet_rotate_keys`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description             | Example Value    |
| :------------- | :------- | :------- | :---------------------- | :--------------- |
| `user_id`      | `string` | Yes      | Wallet owner user ID    | `"agent_001"`    |
| `reason`       | `string` | No       | Rotation reason         | `"policy"`       |

### 4. Output Schema (Return Value)

| Field Name           | Type     | Description              | Example Value              |
| :------------------- | :------- | :----------------------- | :------------------------- |
| `new_wallet_address` | `string` | New wallet address       | `"0xaa11bb22..."` |
| `reason`             | `string` | Rotation reason          | `"policy"`                 |
| `status`             | `string` | Operation result         | `"success"`                |

### 5. Error Handling

- `WALLET_NOT_FOUND`: User has no wallet.
- `KEY_STORAGE_FAILED`: New key could not be stored.

### 6. Idempotency

- **Idempotent**: No. Each call generates new key material.

### 7. Usage Examples

```json
{
  "tool_name": "wallet_rotate_keys",
  "arguments": {
    "user_id": "agent_001",
    "reason": "scheduled"
  }
}
```

### 8. Security Considerations

- **Data Handling**: Old key material is overwritten. New key stored with 0o600 permissions.

---

## Tool: `wallet_backup`

### 1. Tool Purpose and Description

Creates an encrypted backup snapshot of a user's wallet metadata. Returns hashes and metadata only.

### 2. Invocation Name

`wallet_backup`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description          | Example Value   |
| :------------- | :------- | :------- | :------------------- | :-------------- |
| `user_id`      | `string` | Yes      | Wallet owner user ID | `"agent_001"`   |

### 4. Output Schema (Return Value)

| Field Name  | Type     | Description              | Example Value                            |
| :---------- | :------- | :----------------------- | :--------------------------------------- |
| `wallet_id` | `string` | Wallet address           | `"0x1a2b3c..."`                        |
| `key_hash`  | `string` | SHA-256 hash of key      | `"e3b0c44298fc1c14..."` |
| `backup_ts` | `string` | ISO 8601 timestamp       | `"2026-02-04T12:00:00+00:00"`           |
| `status`    | `string` | Operation result         | `"success"`                              |

### 5. Error Handling

- `WALLET_NOT_FOUND`: User has no wallet.

### 6. Idempotency

- **Idempotent**: Partially. Same key produces same hash, but timestamp differs.

### 7. Usage Examples

```json
{
  "tool_name": "wallet_backup",
  "arguments": {
    "user_id": "agent_001"
  }
}
```

### 8. Security Considerations

- **Data Handling**: Only key hash is returned, never raw key material.
- **File Paths**: Backup files stored with 0o600 permissions in designated backup directory.

---

## Tool: `wallet_recover`

### 1. Tool Purpose and Description

Attempts Natural Ritual recovery by verifying a sequence of secret knowledge responses.

### 2. Invocation Name

`wallet_recover`

### 3. Input Schema (Parameters)

| Parameter Name | Type            | Required | Description                    | Example Value          |
| :------------- | :-------------- | :------- | :----------------------------- | :--------------------- |
| `user_id`      | `string`        | Yes      | User attempting recovery       | `"agent_001"`          |
| `responses`    | `array[string]` | Yes      | Answers to ritual prompts      | `["Red", "Cat"]`       |

### 4. Output Schema (Return Value)

| Field Name           | Type      | Description                   | Example Value |
| :------------------- | :-------- | :---------------------------- | :------------ |
| `recovered`          | `boolean` | Whether recovery succeeded    | `true`        |
| `remaining_attempts` | `integer` | Attempts left before lockout  | `3`           |
| `status`             | `string`  | Operation result              | `"success"`   |

### 5. Error Handling

- `NO_RITUAL`: No ritual registered for user.
- `LOCKED_OUT`: User has exhausted all recovery attempts.

### 6. Idempotency

- **Idempotent**: No. Each call consumes an attempt on failure.

### 7. Usage Examples

```json
{
  "tool_name": "wallet_recover",
  "arguments": {
    "user_id": "agent_001",
    "responses": ["MySecretColor", "MySecretAnimal"]
  }
}
```

### 8. Security Considerations

- **Input Validation**: Responses are hashed immediately, never stored in plaintext.
- **Rate Limiting**: Built-in lockout after configurable number of failed attempts (default: 5).
- **Data Handling**: Failed attempt details are logged but do not reveal which step failed to the caller.
