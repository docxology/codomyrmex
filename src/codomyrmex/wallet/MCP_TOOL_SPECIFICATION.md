# Wallet - MCP Tool Specification

## General Considerations for Wallet Tools

- **Registration**: Tools are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.
- **Dependencies**: The tools use `WalletManager`, which stores keys through the `encryption` module's `KeyManager`.
- **No shared registry**: Each call creates a new `WalletManager`. Keys written under `storage_path` persist on disk, but the user-to-address registry does not, so `wallet_get_address` and `wallet_list` do not see wallets created by earlier calls. Pass `wallet_address` to `wallet_generate_zk_proof` for a wallet created by a previous call.
- **Error Handling**: Tools return `{"status": "error", "message": "<description>"}` on failure.
- **Security**: Private keys are never returned. Signing, key rotation, backup and recovery are available from the Python API only, not as MCP tools.

---

## Tool: `wallet_create`

### 1. Tool Purpose and Description

Creates a self-custody wallet for a user and stores its private key through `KeyManager`.

### 2. Invocation Name

`wallet_create`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `string` | Yes | Unique identifier for wallet owner | `"agent_001"` |
| `storage_path` | `string` | No | Key storage directory path | `"/tmp/keys"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `user_id` | `string` | Owner user ID | `"agent_001"` |
| `wallet_address` | `string` | Generated 0x-prefixed address | `"0x35edfcae24784395838d37029f733c08"` |

### 5. Idempotency

- **Idempotent**: No. Each call generates a new key and address.

### 6. Usage Examples

```json
{
  "tool_name": "wallet_create",
  "arguments": {
    "user_id": "agent_001",
    "storage_path": "/tmp/keys"
  }
}
```

### 7. Security Considerations

- **Permissions**: Requires write access to the key storage directory.

---

## Tool: `wallet_get_address`

### 1. Tool Purpose and Description

Reports whether a user has a wallet in the manager's registry and returns its address.

### 2. Invocation Name

`wallet_get_address`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `string` | Yes | The user identifier | `"agent_001"` |
| `storage_path` | `string` | No | Key storage directory path | `"/tmp/keys"` |

### 4. Output Schema (Return Value)

```json
{"status": "success", "user_id": "agent_001", "has_wallet": false, "wallet_address": null}
```

---

## Tool: `wallet_list`

### 1. Tool Purpose and Description

Lists the wallets in the manager's registry as a mapping of user IDs to addresses.

### 2. Invocation Name

`wallet_list`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `storage_path` | `string` | No | Key storage directory path | `"/tmp/keys"` |

### 4. Output Schema (Return Value)

```json
{"status": "success", "wallets": {}, "count": 0}
```

---

## Tool: `wallet_generate_zk_proof`

### 1. Tool Purpose and Description

Generates a non-interactive (Fiat-Shamir, HMAC-SHA256) proof that the caller holds the wallet's private key, without revealing the key.

### 2. Invocation Name

`wallet_generate_zk_proof`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `string` | Yes | Wallet owner | `"agent_001"` |
| `storage_path` | `string` | No | Key storage directory path | `"/tmp/keys"` |
| `message` | `string` | No | Message the proof covers, e.g. a transaction hash (default `""`) | `"tx1"` |
| `wallet_address` | `string` | No | Wallet address; needed for a wallet created by a previous call | `"0x35edfcae24784395838d37029f733c08"` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "proof": {
    "user_id": "agent_001",
    "wallet_address": "0x35edfcae24784395838d37029f733c08",
    "challenge": "<hex>",
    "response": "<hex>",
    "message": "747831",
    "timestamp": "2026-10-07T23:41:30.545732+00:00",
    "nonce": "<hex>"
  }
}
```

An unknown wallet returns `{"status": "error", "message": "[WalletNotFoundError] Wallet not found: <user_id>"}`.

---

## Tool: `wallet_verify_zk_proof`

### 1. Tool Purpose and Description

Verifies a proof from `wallet_generate_zk_proof` by re-deriving the challenge and checking the HMAC response.

### 2. Invocation Name

`wallet_verify_zk_proof`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `proof` | `object` | Yes | The `proof` object from `wallet_generate_zk_proof` | see above |
| `storage_path` | `string` | No | Key storage directory path | `"/tmp/keys"` |
| `message` | `string` | No | The message the proof covers (default `""`) | `"tx1"` |

### 4. Output Schema (Return Value)

```json
{"status": "success", "verified": true}
```

### 5. Idempotency

- **Idempotent**: Yes

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
