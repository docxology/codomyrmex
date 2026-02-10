# Smart Contracts - API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Smart Contracts module provides blockchain contract interfaces, transaction building, ABI parsing, and unit conversion utilities. Supports Ethereum-compatible networks and Solana.

## Enums

### `Network`

Supported blockchain networks.

- `Network.ETHEREUM` - Ethereum mainnet
- `Network.POLYGON` - Polygon PoS
- `Network.ARBITRUM` - Arbitrum One
- `Network.OPTIMISM` - Optimism
- `Network.BASE` - Base
- `Network.SOLANA` - Solana

### `TransactionStatus`

Transaction lifecycle states.

- `TransactionStatus.PENDING` - Submitted but not confirmed
- `TransactionStatus.CONFIRMED` - Included in a block
- `TransactionStatus.FAILED` - Reverted or rejected

## Data Classes

### `Address`

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `value` | `str` | required | Raw address string |
| `network` | `Network` | `Network.ETHEREUM` | Target network |

#### Property: `is_valid -> bool`

Returns `True` for EVM networks if value is 42 chars starting with `0x`. For Solana, checks non-empty.

### `Transaction`

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `hash` | `str` | required | Transaction hash |
| `from_address` | `Address` | required | Sender address |
| `to_address` | `Address` | required | Recipient address |
| `value` | `int` | required | Value in wei/lamports |
| `data` | `str` | `""` | Encoded calldata |
| `gas_limit` | `int` | `21000` | Gas limit |
| `gas_price` | `int` | `0` | Gas price in wei |
| `nonce` | `int` | `0` | Sender nonce |
| `status` | `TransactionStatus` | `PENDING` | Current status |
| `block_number` | `int | None` | `None` | Block inclusion number |
| `timestamp` | `datetime` | `now()` | Creation timestamp |

### `ContractFunction`

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `name` | `str` | required | Function name |
| `inputs` | `list[dict[str, str]]` | `[]` | Input parameters (`{name, type}`) |
| `outputs` | `list[dict[str, str]]` | `[]` | Output parameters (`{name, type}`) |
| `payable` | `bool` | `False` | Accepts ETH |
| `view` | `bool` | `False` | Read-only call |

#### `ContractFunction.encode_call(*args) -> str`

- **Description**: Encode function selector (simplified SHA3 of signature, first 8 hex chars).
- **Returns**: `str` - `0x`-prefixed selector string.

### `Contract`

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `address` | `Address` | required | Deployed contract address |
| `abi` | `list[dict[str, Any]]` | `[]` | Contract ABI array |
| `name` | `str` | `""` | Human-readable name |

ABI is parsed at initialization. Only items with `"type": "function"` are indexed.

#### `Contract.get_function(name) -> ContractFunction | None`

- **Description**: Look up a parsed function by name.

#### `Contract.list_functions() -> list[str]`

- **Description**: Return all function names found in the ABI.

## Classes

### `ContractCall`

Fluent builder for contract function calls.

#### `ContractCall.__init__(contract, function_name)`

- **Parameters**:
    - `contract` (Contract): Target contract.
    - `function_name` (str): Function to call.

#### `ContractCall.with_args(*args) -> ContractCall`

Set call arguments. Returns self.

#### `ContractCall.with_value(value) -> ContractCall`

Set ETH value in wei. Returns self.

#### `ContractCall.with_gas_limit(limit) -> ContractCall`

Override gas limit (default: 100000). Returns self.

#### `ContractCall.encode() -> str`

- **Description**: Encode the function call data.
- **Raises**: `ValueError` if function name is not found in the contract ABI.

#### `ContractCall.to_transaction(from_address, nonce=0) -> Transaction`

- **Description**: Build a `Transaction` object for this call.
- **Parameters**:
    - `from_address` (Address): Sender.
    - `nonce` (int): Sender nonce.

### `TransactionBuilder`

Fluent builder for raw transactions.

#### `TransactionBuilder.__init__(from_address)`

- **Parameters**:
    - `from_address` (Address): Sender address.

#### Builder Methods (all return `self`)

- `to(address) -> TransactionBuilder` - Set recipient.
- `value(amount) -> TransactionBuilder` - Set value in wei.
- `data(data) -> TransactionBuilder` - Set calldata.
- `gas_limit(limit) -> TransactionBuilder` - Set gas limit.
- `gas_price(price) -> TransactionBuilder` - Set gas price.
- `nonce(nonce) -> TransactionBuilder` - Set nonce.

#### `TransactionBuilder.build() -> Transaction`

- **Description**: Construct the `Transaction`. Generates a deterministic hash from sender, recipient, value, and nonce.
- **Raises**: `ValueError` if `to` address was not set.

### `ContractRegistry`

In-memory registry of named contracts.

#### `ContractRegistry.register(name, contract) -> None`

Register a contract by name.

#### `ContractRegistry.get(name) -> Contract | None`

Look up a contract by name.

#### `ContractRegistry.remove(name) -> bool`

Remove a contract by name. Returns `True` if it existed, `False` otherwise.

#### `ContractRegistry.list() -> list[str]`

Return all registered contract names.

### `ContractEvent`

A smart contract event.

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `name` | `str` | required | Event name (e.g., `"Transfer"`) |
| `args` | `dict[str, Any]` | `{}` | Event arguments |
| `contract_address` | `Address | None` | `None` | Emitting contract |
| `block_number` | `int` | `0` | Block number |
| `transaction_hash` | `str` | `""` | Transaction hash |
| `log_index` | `int` | `0` | Log index |
| `timestamp` | `datetime` | `now()` | Event timestamp |

### `EventFilter`

Fluent builder for filtering contract events.

#### Builder Methods (all return `self`)

- `event(name) -> EventFilter` - Filter by event name.
- `from_block(block) -> EventFilter` - Set minimum block number.
- `to_block(block) -> EventFilter` - Set maximum block number.
- `address(addr) -> EventFilter` - Filter by contract address.

#### `EventFilter.matches(event) -> bool`

Check if a `ContractEvent` matches all filter criteria.

### `EventLog`

Collect and query contract events.

#### `EventLog.add(event) -> None`

Add a `ContractEvent` to the log.

#### `EventLog.query(filter=None) -> list[ContractEvent]`

Query events with optional `EventFilter`. Returns all events if no filter provided.

#### `EventLog.count(event_name=None) -> int`

Count events, optionally filtered by event name.

#### `EventLog.latest(n=1) -> list[ContractEvent]`

Get the `n` most recent events sorted by block number (descending).

## Utility Functions

### `wei_to_ether(wei) -> float`

Convert wei to ether (`wei / 10^18`).

### `ether_to_wei(ether) -> int`

Convert ether to wei (`int(ether * 10^18)`).

### `gwei_to_wei(gwei) -> int`

Convert gwei to wei (`int(gwei * 10^9)`).

## Error Handling

- `ValueError` is raised by `ContractCall.encode()` for unknown functions and by `TransactionBuilder.build()` for missing recipient.
- No custom exception classes. Standard Python exceptions only.

## Configuration

No external configuration files. All parameters are passed at construction time. Network selection is per-`Address`.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
