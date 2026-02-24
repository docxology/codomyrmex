# crypto/currency -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `crypto/currency` submodule provides cryptocurrency operations: BIP-32/BIP-39 HD wallets, blockchain primitives (blocks, Merkle trees), transaction creation/signing/verification, Bitcoin and Ethereum address generation/validation, and ERC-20 token interface encoding.

## When to Use This Module

- You need to generate BIP-39 mnemonics or derive HD wallet keys (BIP-32)
- You need to create, hash, or validate blockchain blocks
- You need to build or verify Merkle trees and Merkle proofs
- You need to create, sign, verify, serialize, or deserialize transactions
- You need to generate or validate Bitcoin or Ethereum addresses
- You need to encode ERC-20 transfer calls or decode transfer events

## Exports

**Wallet (BIP-32/BIP-39):**

| Name | Kind | Purpose |
|------|------|---------|
| `generate_mnemonic` | function | Generate BIP-39 mnemonic phrase |
| `mnemonic_to_seed` | function | Convert mnemonic to seed bytes |
| `HDWallet` | class | Hierarchical deterministic wallet |
| `create_hd_wallet` | function | Create HD wallet from mnemonic |

**Blockchain:**

| Name | Kind | Purpose |
|------|------|---------|
| `Block` | dataclass | Block data structure |
| `MerkleTree` / `MerkleProof` | dataclass | Merkle tree and proof containers |
| `create_block` | function | Create a new block |
| `calculate_block_hash` | function | Compute block hash |
| `build_merkle_tree` | function | Build Merkle tree from transaction list |
| `get_merkle_proof` / `verify_merkle_proof` | function | Generate and verify Merkle proofs |

**Transactions:**

| Name | Kind | Purpose |
|------|------|---------|
| `Transaction` / `SignedTransaction` | dataclass | Transaction containers |
| `create_transaction` | function | Create unsigned transaction |
| `sign_transaction` / `verify_transaction` | function | Sign and verify transactions |
| `serialize_transaction` / `deserialize_transaction` | function | Transaction serialization |

**Addresses:**

| Name | Kind | Purpose |
|------|------|---------|
| `generate_bitcoin_address` / `validate_bitcoin_address` | function | Bitcoin address operations |
| `generate_ethereum_address` / `validate_ethereum_address` | function | Ethereum address operations |
| `checksum_ethereum_address` | function | EIP-55 checksum encoding |

**Tokens:**

| Name | Kind | Purpose |
|------|------|---------|
| `ERC20Token` / `TransferEvent` | dataclass | Token and event containers |
| `create_erc20_interface` | function | Create ERC-20 interface descriptor |
| `encode_transfer` | function | Encode ERC-20 transfer call data |
| `decode_transfer_event` | function | Decode ERC-20 Transfer event log |

## Example Agent Usage

```python
from codomyrmex.crypto.currency import (
    generate_mnemonic, create_hd_wallet,
    generate_bitcoin_address, validate_bitcoin_address,
    create_transaction, sign_transaction, verify_transaction,
    build_merkle_tree, get_merkle_proof, verify_merkle_proof,
)

# HD wallet
mnemonic = generate_mnemonic()
wallet = create_hd_wallet(mnemonic)

# Bitcoin address
addr = generate_bitcoin_address(wallet.public_key)
assert validate_bitcoin_address(addr)

# Transactions
tx = create_transaction(sender="addr1", receiver="addr2", amount=1.5)
signed = sign_transaction(tx, wallet.private_key)
assert verify_transaction(signed)

# Merkle tree
tree = build_merkle_tree(["tx1", "tx2", "tx3", "tx4"])
proof = get_merkle_proof(tree, "tx2")
assert verify_merkle_proof(proof, tree.root)
```

## Constraints

- HD wallet operations follow BIP-32/BIP-39 standards.
- Bitcoin addresses use Base58Check encoding; Ethereum uses hex with EIP-55 checksums.
- ERC-20 encoding follows the Solidity ABI specification.
- These are cryptographic primitives, not a full blockchain node or wallet application.

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `crypto.encoding` | Base58 encoding used by Bitcoin addresses |
| `crypto.graphy` | Key pair generation and hashing underpin wallet and transaction operations |
| `crypto.protocols` | Key exchange protocols can complement multi-party transaction signing |
