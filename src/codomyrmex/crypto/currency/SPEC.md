# Crypto Currency -- Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Cryptocurrency primitives covering BIP-32/BIP-39 HD wallets, blockchain data structures (blocks, Merkle trees), transaction construction and signing, multi-chain address generation and validation, and ERC-20 token interfaces.

## Architecture

```
crypto/currency/
├── __init__.py        # 27 re-exports across 5 submodules
├── wallet.py          # BIP-32/39 HD wallets, mnemonic generation
├── blockchain.py      # Block, MerkleTree, MerkleProof, block hashing
├── transactions.py    # Transaction creation, signing, verification, serialization
├── addresses.py       # Bitcoin/Ethereum address generation and validation
└── tokens.py          # ERC-20 token interface, transfer encoding/decoding
```

## Key Classes and Functions

### wallet.py

| Name | Kind | Description |
|------|------|-------------|
| `HDWallet` | class | Hierarchical deterministic wallet (BIP-32) |
| `generate_mnemonic` | function | Generate BIP-39 mnemonic seed phrase |
| `mnemonic_to_seed` | function | Derive seed bytes from mnemonic and optional passphrase |
| `create_hd_wallet` | function | Create an HDWallet from a mnemonic |

### blockchain.py

| Name | Kind | Description |
|------|------|-------------|
| `Block` | dataclass | Block data structure with header, transactions, hash |
| `MerkleTree` | class | Binary Merkle tree for transaction commitment |
| `MerkleProof` | dataclass | Inclusion proof for a leaf in a Merkle tree |
| `create_block` | function | Construct a new block from transactions |
| `calculate_block_hash` | function | Compute SHA-256 block hash from header fields |
| `build_merkle_tree` | function | Build a Merkle tree from a list of transaction hashes |
| `get_merkle_proof` | function | Generate an inclusion proof for a given leaf |
| `verify_merkle_proof` | function | Verify a Merkle inclusion proof against a root hash |

### transactions.py

| Name | Kind | Description |
|------|------|-------------|
| `Transaction` | dataclass | Unsigned transaction with inputs, outputs, metadata |
| `SignedTransaction` | dataclass | Transaction with attached signature |
| `create_transaction` | function | Build an unsigned transaction |
| `sign_transaction` | function | Sign a transaction with a private key |
| `verify_transaction` | function | Verify a signed transaction's signature |
| `serialize_transaction` | function | Serialize a transaction to bytes |
| `deserialize_transaction` | function | Deserialize bytes to a Transaction |

### addresses.py

| Name | Kind | Description |
|------|------|-------------|
| `generate_bitcoin_address` | function | Derive a Bitcoin address from a public key |
| `validate_bitcoin_address` | function | Validate a Bitcoin address (format and checksum) |
| `generate_ethereum_address` | function | Derive an Ethereum address from a public key |
| `validate_ethereum_address` | function | Validate an Ethereum address format |
| `checksum_ethereum_address` | function | Apply EIP-55 mixed-case checksum to an Ethereum address |

### tokens.py

| Name | Kind | Description |
|------|------|-------------|
| `ERC20Token` | dataclass | ERC-20 token metadata (name, symbol, decimals, address) |
| `TransferEvent` | dataclass | Decoded ERC-20 Transfer event log |
| `create_erc20_interface` | function | Build an ERC-20 contract interface specification |
| `encode_transfer` | function | ABI-encode an ERC-20 transfer call |
| `decode_transfer_event` | function | Decode a raw Transfer event log into a TransferEvent |

## Dependencies

- `hashlib` (SHA-256 for block hashing, address derivation)
- Python standard library (`struct`, `os.urandom`)
- No external blockchain SDK dependencies

## Constraints

- Mnemonic word count must be one of: 12, 15, 18, 21, 24.
- Bitcoin addresses support P2PKH format only.
- Transaction serialization uses a compact binary format (not Bitcoin wire protocol).

## Error Handling

| Error | When |
|-------|------|
| `ValueError` | Invalid mnemonic length, malformed address, invalid transaction fields |
| `TypeError` | Wrong key type for signing/verification |

## Navigation

- **Parent**: [crypto/SPEC.md](../SPEC.md)
- **Siblings**: [AGENTS.md](AGENTS.md), [README.md](README.md), [PAI.md](PAI.md)
