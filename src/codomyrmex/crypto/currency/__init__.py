"""Cryptocurrency operations: wallets, blockchain, transactions, addresses, tokens.

Public API
----------

Wallet (BIP-32 / BIP-39):
    generate_mnemonic, mnemonic_to_seed, HDWallet, create_hd_wallet

Blockchain primitives:
    Block, MerkleTree, MerkleProof, create_block, calculate_block_hash,
    build_merkle_tree, get_merkle_proof, verify_merkle_proof

Transactions:
    Transaction, SignedTransaction, create_transaction, sign_transaction,
    verify_transaction, serialize_transaction, deserialize_transaction

Addresses:
    generate_bitcoin_address, validate_bitcoin_address,
    generate_ethereum_address, validate_ethereum_address,
    checksum_ethereum_address

Tokens:
    ERC20Token, TransferEvent, create_erc20_interface, encode_transfer,
    decode_transfer_event
"""

from codomyrmex.crypto.currency.wallet import (
    generate_mnemonic,
    mnemonic_to_seed,
    HDWallet,
    create_hd_wallet,
)
from codomyrmex.crypto.currency.blockchain import (
    Block,
    MerkleTree,
    MerkleProof,
    create_block,
    calculate_block_hash,
    build_merkle_tree,
    get_merkle_proof,
    verify_merkle_proof,
)
from codomyrmex.crypto.currency.transactions import (
    Transaction,
    SignedTransaction,
    create_transaction,
    sign_transaction,
    verify_transaction,
    serialize_transaction,
    deserialize_transaction,
)
from codomyrmex.crypto.currency.addresses import (
    generate_bitcoin_address,
    validate_bitcoin_address,
    generate_ethereum_address,
    validate_ethereum_address,
    checksum_ethereum_address,
)
from codomyrmex.crypto.currency.tokens import (
    ERC20Token,
    TransferEvent,
    create_erc20_interface,
    encode_transfer,
    decode_transfer_event,
)

__all__ = [
    # Wallet
    "generate_mnemonic",
    "mnemonic_to_seed",
    "HDWallet",
    "create_hd_wallet",
    # Blockchain
    "Block",
    "MerkleTree",
    "MerkleProof",
    "create_block",
    "calculate_block_hash",
    "build_merkle_tree",
    "get_merkle_proof",
    "verify_merkle_proof",
    # Transactions
    "Transaction",
    "SignedTransaction",
    "create_transaction",
    "sign_transaction",
    "verify_transaction",
    "serialize_transaction",
    "deserialize_transaction",
    # Addresses
    "generate_bitcoin_address",
    "validate_bitcoin_address",
    "generate_ethereum_address",
    "validate_ethereum_address",
    "checksum_ethereum_address",
    # Tokens
    "ERC20Token",
    "TransferEvent",
    "create_erc20_interface",
    "encode_transfer",
    "decode_transfer_event",
]
