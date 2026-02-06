# Smart Contracts - MCP Tool Specification

## General Considerations for Smart Contracts Tools

- **Dependencies**: No external dependencies (no web3.py). Pure Python with `hashlib` and standard library.
- **Initialization**: `ContractRegistry` is maintained across tool calls within a session for contract lookups.
- **Error Handling**: Tools return `{"error": "description"}` on failure. Invalid addresses and unknown functions produce descriptive errors.
- **Networks**: All EVM-compatible networks use the same address validation (42 chars, `0x` prefix). Solana addresses use non-empty validation only.

---

## Tool: `contract_call`

### 1. Tool Purpose and Description

Executes a read or write call against a registered smart contract function. For view functions, returns the simulated result. For state-changing functions, builds and returns the unsigned transaction.

### 2. Invocation Name

`contract_call`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `contract_name` | `string` | Yes | Name of a registered contract | `"USDC"` |
| `function_name` | `string` | Yes | Contract function to call | `"balanceOf"` |
| `args` | `array` | No | Function arguments | `["0x1234...abcd"]` |
| `from_address` | `string` | No | Sender address (required for write calls) | `"0xabcd...1234"` |
| `value_wei` | `integer` | No | ETH value to send in wei. Default: `0` | `1000000000000000000` |
| `gas_limit` | `integer` | No | Gas limit override. Default: `100000` | `200000` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `function` | `string` | Called function name | `"balanceOf"` |
| `encoded_data` | `string` | Encoded calldata | `"0xa9059cbb"` |
| `is_view` | `boolean` | Whether this is a read-only call | `true` |
| `transaction` | `object | null` | Transaction object if write call, null if view | See below |
| `status` | `string` | Operation result | `"success"` |

### 5. Error Handling

- `CONTRACT_NOT_FOUND`: No contract registered with the given name.
- `FUNCTION_NOT_FOUND`: Function name not in the contract ABI.
- `MISSING_SENDER`: Write call requires `from_address`.
- `INVALID_ADDRESS`: Address format is invalid for the contract's network.

### 6. Idempotency

- **Idempotent**: Yes for view calls. Write calls generate a new transaction hash each time.

### 7. Usage Examples

```json
{
  "tool_name": "contract_call",
  "arguments": {
    "contract_name": "USDC",
    "function_name": "balanceOf",
    "args": ["0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"]
  }
}
```

```json
{
  "tool_name": "contract_call",
  "arguments": {
    "contract_name": "USDC",
    "function_name": "transfer",
    "args": ["0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18", "1000000"],
    "from_address": "0xabcdef0123456789abcdef0123456789abcdef01",
    "gas_limit": 150000
  }
}
```

### 8. Security Considerations

- **Input Validation**: Addresses are validated against network format. Function names are checked against ABI.
- **Data Handling**: No private keys are handled. Transactions are returned unsigned.
- **Permissions**: Write calls require explicit `from_address`. No automatic signing.

---

## Tool: `contract_deploy`

### 1. Tool Purpose and Description

Builds an unsigned deployment transaction for a smart contract given its ABI and bytecode. Registers the contract in the session registry upon construction.

### 2. Invocation Name

`contract_deploy`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `name` | `string` | Yes | Registry name for the contract | `"MyToken"` |
| `abi` | `array` | Yes | Contract ABI JSON array | `[{"type": "function", ...}]` |
| `from_address` | `string` | Yes | Deployer address | `"0xabcd...1234"` |
| `network` | `string` | No | Target network. Default: `"ethereum"` | `"polygon"` |
| `value_wei` | `integer` | No | ETH to send with deployment. Default: `0` | `0` |
| `gas_limit` | `integer` | No | Gas limit. Default: `3000000` | `5000000` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `name` | `string` | Registered contract name | `"MyToken"` |
| `network` | `string` | Target network | `"ethereum"` |
| `functions` | `array[string]` | Parsed function names from ABI | `["transfer", "balanceOf"]` |
| `transaction` | `object` | Unsigned deployment transaction | See below |
| `status` | `string` | Operation result | `"success"` |

### 5. Error Handling

- `INVALID_ABI`: ABI is not a valid JSON array.
- `INVALID_ADDRESS`: Deployer address format is invalid.
- `INVALID_NETWORK`: Network name is not recognized.

### 6. Idempotency

- **Idempotent**: No. Each call generates a new transaction hash and overwrites the registry entry.

### 7. Usage Examples

```json
{
  "tool_name": "contract_deploy",
  "arguments": {
    "name": "SimpleStorage",
    "abi": [
      {
        "type": "function",
        "name": "store",
        "inputs": [{"name": "value", "type": "uint256"}],
        "outputs": [],
        "stateMutability": "nonpayable"
      },
      {
        "type": "function",
        "name": "retrieve",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view"
      }
    ],
    "from_address": "0xabcdef0123456789abcdef0123456789abcdef01",
    "network": "polygon"
  }
}
```

### 8. Security Considerations

- **Input Validation**: ABI is parsed and validated. Only `"type": "function"` entries are indexed.
- **Data Handling**: No bytecode execution. Transaction is returned unsigned.
- **Permissions**: Deployer address is recorded but no signing occurs.

---

## Tool: `transaction_status`

### 1. Tool Purpose and Description

Checks the current status of a transaction by hash. Returns status, block number, and gas details.

### 2. Invocation Name

`transaction_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `tx_hash` | `string` | Yes | Transaction hash (`0x`-prefixed) | `"0xabc123..."` |
| `network` | `string` | No | Network to query. Default: `"ethereum"` | `"arbitrum"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `hash` | `string` | Transaction hash | `"0xabc123..."` |
| `status` | `string` | One of: `pending`, `confirmed`, `failed` | `"confirmed"` |
| `block_number` | `integer | null` | Block number if confirmed | `18500000` |
| `from_address` | `string` | Sender address | `"0xabcd..."` |
| `to_address` | `string` | Recipient address | `"0x1234..."` |
| `value_wei` | `integer` | Transaction value in wei | `1000000000000000000` |
| `gas_used` | `integer` | Gas consumed | `21000` |

### 5. Error Handling

- `TX_NOT_FOUND`: Transaction hash not found on the specified network.
- `INVALID_HASH`: Hash is not a valid `0x`-prefixed hex string.
- `INVALID_NETWORK`: Network name is not recognized.

### 6. Idempotency

- **Idempotent**: Yes. Read-only status query.

### 7. Usage Examples

```json
{
  "tool_name": "transaction_status",
  "arguments": {
    "tx_hash": "0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd",
    "network": "ethereum"
  }
}
```

### 8. Security Considerations

- **Data Handling**: Read-only query. No private data exposed.
- **Input Validation**: Hash format is validated before lookup.

---

## Tool: `contract_abi`

### 1. Tool Purpose and Description

Retrieves the parsed ABI for a registered contract, listing all available functions with their input/output signatures and mutability.

### 2. Invocation Name

`contract_abi`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `contract_name` | `string` | Yes | Name of a registered contract | `"USDC"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `name` | `string` | Contract name | `"USDC"` |
| `address` | `string` | Contract address | `"0xA0b8..."` |
| `network` | `string` | Deployed network | `"ethereum"` |
| `functions` | `array[object]` | List of `{name, inputs, outputs, payable, view}` | See below |
| `function_count` | `integer` | Total parsed functions | `8` |

### 5. Error Handling

- `CONTRACT_NOT_FOUND`: No contract registered with the given name.

### 6. Idempotency

- **Idempotent**: Yes. Read-only registry lookup.

### 7. Usage Examples

```json
{
  "tool_name": "contract_abi",
  "arguments": {
    "contract_name": "USDC"
  }
}
```

### 8. Security Considerations

- **Data Handling**: Read-only. ABI data contains no sensitive information.

---

## Navigation Links

- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Human Documentation**: [README.md](README.md)
- **Parent Directory**: [codomyrmex](../README.md)
