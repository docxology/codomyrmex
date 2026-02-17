"""Blockchain primitives: blocks, Merkle trees, and proof verification.

Provides data structures and functions for creating blocks, computing block
hashes, building Merkle trees from transaction data, and verifying Merkle
inclusion proofs.

Note:
    This is an educational/reference implementation demonstrating core
    blockchain concepts. It is not a full consensus-ready blockchain.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

from codomyrmex.crypto.exceptions import BlockchainError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class Block:
    """A single block in the chain.

    Attributes:
        index: Position in the chain (0 = genesis).
        timestamp: Unix timestamp when the block was created.
        data: Arbitrary payload (transaction data, etc.).
        previous_hash: Hash of the preceding block.
        nonce: Proof-of-work nonce.
        hash: SHA-256 hash of this block.
    """

    index: int
    timestamp: float
    data: str
    previous_hash: str
    nonce: int = 0
    hash: str = ""


@dataclass
class MerkleTree:
    """Binary hash tree built from a list of leaf hashes.

    Attributes:
        root: The Merkle root hash.
        leaves: Original leaf hashes.
        levels: All levels of the tree (``levels[0]`` = leaves,
            ``levels[-1]`` = ``[root]``).
    """

    root: bytes
    leaves: list[bytes]
    levels: list[list[bytes]]


@dataclass
class MerkleProof:
    """Inclusion proof for a single leaf in a Merkle tree.

    Attributes:
        leaf: The leaf hash being proven.
        proof: Sequence of ``(sibling_hash, position)`` pairs where
            *position* is ``"left"`` or ``"right"`` indicating the
            sibling's side.
        root: Expected Merkle root.
    """

    leaf: bytes
    proof: list[tuple[bytes, str]]
    root: bytes


# ---------------------------------------------------------------------------
# Block functions
# ---------------------------------------------------------------------------


def calculate_block_hash(block: Block) -> str:
    """Compute the SHA-256 hash of a block.

    The hash is derived from the concatenation of the block's index,
    timestamp, data, previous hash, and nonce.

    Args:
        block: The block to hash.

    Returns:
        Hex-encoded SHA-256 digest.
    """
    content = (
        str(block.index)
        + str(block.timestamp)
        + block.data
        + block.previous_hash
        + str(block.nonce)
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def create_block(index: int, data: str, previous_hash: str) -> Block:
    """Create a new block with a computed hash.

    Args:
        index: Block position in the chain.
        data: Block payload.
        previous_hash: Hash of the previous block.

    Returns:
        A fully populated ``Block`` instance.

    Raises:
        BlockchainError: If block creation fails.
    """
    try:
        block = Block(
            index=index,
            timestamp=time.time(),
            data=data,
            previous_hash=previous_hash,
        )
        block.hash = calculate_block_hash(block)
        logger.debug("Created block index=%d hash=%s", index, block.hash[:16])
        return block
    except Exception as exc:
        raise BlockchainError(f"Block creation failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Merkle tree functions
# ---------------------------------------------------------------------------


def _merkle_hash_pair(left: bytes, right: bytes) -> bytes:
    """Hash a pair of nodes: SHA-256(left || right)."""
    return hashlib.sha256(left + right).digest()


def build_merkle_tree(leaves: list[bytes]) -> MerkleTree:
    """Build a binary Merkle tree from a list of leaf hashes.

    If the number of nodes at any level is odd, the last node is duplicated
    before hashing.

    Args:
        leaves: List of leaf hashes (each should be raw bytes, typically
            32-byte SHA-256 digests).

    Returns:
        A ``MerkleTree`` containing the root, original leaves, and all
        intermediate levels.

    Raises:
        BlockchainError: If the leaves list is empty.
    """
    if not leaves:
        raise BlockchainError("Cannot build Merkle tree from empty leaf list")

    levels: list[list[bytes]] = [list(leaves)]
    current_level = list(leaves)

    while len(current_level) > 1:
        next_level: list[bytes] = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            next_level.append(_merkle_hash_pair(left, right))
        levels.append(next_level)
        current_level = next_level

    root = current_level[0]
    logger.debug(
        "Built Merkle tree with %d leaves, root=%s",
        len(leaves),
        root.hex()[:16],
    )
    return MerkleTree(root=root, leaves=list(leaves), levels=levels)


def get_merkle_proof(tree: MerkleTree, leaf_index: int) -> MerkleProof:
    """Extract an inclusion proof for a specific leaf.

    Args:
        tree: A previously built ``MerkleTree``.
        leaf_index: Zero-based index of the leaf in the original list.

    Returns:
        A ``MerkleProof`` for the given leaf.

    Raises:
        BlockchainError: If the index is out of range.
    """
    if leaf_index < 0 or leaf_index >= len(tree.leaves):
        raise BlockchainError(
            f"Leaf index {leaf_index} out of range [0, {len(tree.leaves)})"
        )

    proof: list[tuple[bytes, str]] = []
    idx = leaf_index

    for level in tree.levels[:-1]:  # skip the root level
        if idx % 2 == 0:
            # sibling is on the right
            sibling_idx = idx + 1
            if sibling_idx < len(level):
                proof.append((level[sibling_idx], "right"))
            else:
                # odd count -- sibling is a duplicate of self
                proof.append((level[idx], "right"))
        else:
            # sibling is on the left
            proof.append((level[idx - 1], "left"))
        idx //= 2

    return MerkleProof(
        leaf=tree.leaves[leaf_index],
        proof=proof,
        root=tree.root,
    )


def verify_merkle_proof(
    leaf: bytes,
    proof: list[tuple[bytes, str]],
    root: bytes,
) -> bool:
    """Verify a Merkle inclusion proof.

    Args:
        leaf: The leaf hash to verify.
        proof: List of ``(sibling_hash, position)`` pairs.
        root: The expected Merkle root.

    Returns:
        ``True`` if the proof is valid, ``False`` otherwise.
    """
    current = leaf
    for sibling, position in proof:
        if position == "left":
            current = _merkle_hash_pair(sibling, current)
        else:
            current = _merkle_hash_pair(current, sibling)

    valid = current == root
    logger.debug("Merkle proof verification: %s", "valid" if valid else "INVALID")
    return valid
