"""Unit tests for codomyrmex.crypto.currency.blockchain."""

from __future__ import annotations

import hashlib

import pytest

from codomyrmex.crypto.currency.blockchain import (
    Block,
    create_block,
    calculate_block_hash,
    build_merkle_tree,
    get_merkle_proof,
    verify_merkle_proof,
)
from codomyrmex.crypto.exceptions import BlockchainError


pytestmark = [pytest.mark.crypto, pytest.mark.unit]


# ---------------------------------------------------------------------------
# Block tests
# ---------------------------------------------------------------------------


class TestBlockCreation:
    """Tests for block creation and hash computation."""

    def test_create_block_sets_index(self):
        """Test functionality: create block sets index."""
        block = create_block(0, "genesis", "0" * 64)
        assert block.index == 0

    def test_create_block_computes_hash(self):
        """Test functionality: create block computes hash."""
        block = create_block(0, "genesis", "0" * 64)
        assert block.hash
        assert len(block.hash) == 64  # SHA-256 hex digest

    def test_hash_is_deterministic_for_same_block(self):
        """Test functionality: hash is deterministic for same block."""
        block = Block(
            index=1,
            timestamp=1000000.0,
            data="test",
            previous_hash="abc",
            nonce=42,
        )
        h1 = calculate_block_hash(block)
        h2 = calculate_block_hash(block)
        assert h1 == h2

    def test_different_data_different_hash(self):
        """Test functionality: different data different hash."""
        b1 = Block(index=0, timestamp=1.0, data="A", previous_hash="0")
        b2 = Block(index=0, timestamp=1.0, data="B", previous_hash="0")
        assert calculate_block_hash(b1) != calculate_block_hash(b2)

    def test_different_nonce_different_hash(self):
        """Test functionality: different nonce different hash."""
        b1 = Block(index=0, timestamp=1.0, data="X", previous_hash="0", nonce=0)
        b2 = Block(index=0, timestamp=1.0, data="X", previous_hash="0", nonce=1)
        assert calculate_block_hash(b1) != calculate_block_hash(b2)


# ---------------------------------------------------------------------------
# Merkle tree tests
# ---------------------------------------------------------------------------


def _leaf(data: str) -> bytes:
    """Helper to create a SHA-256 leaf hash."""
    return hashlib.sha256(data.encode()).digest()


class TestMerkleTree:
    """Tests for Merkle tree construction."""

    def test_single_leaf_root_equals_leaf(self):
        """Test functionality: single leaf root equals leaf."""
        leaves = [_leaf("a")]
        tree = build_merkle_tree(leaves)
        assert tree.root == leaves[0]

    def test_two_leaves_root_is_hash_of_pair(self):
        """Test functionality: two leaves root is hash of pair."""
        a, b = _leaf("a"), _leaf("b")
        tree = build_merkle_tree([a, b])
        expected = hashlib.sha256(a + b).digest()
        assert tree.root == expected

    def test_four_leaves_known_structure(self):
        """Test functionality: four leaves known structure."""
        leaves = [_leaf(c) for c in "abcd"]
        tree = build_merkle_tree(leaves)

        ab = hashlib.sha256(leaves[0] + leaves[1]).digest()
        cd = hashlib.sha256(leaves[2] + leaves[3]).digest()
        root = hashlib.sha256(ab + cd).digest()
        assert tree.root == root

    def test_odd_leaf_count_duplicates_last(self):
        """Test functionality: odd leaf count duplicates last."""
        leaves = [_leaf(c) for c in "abc"]
        tree = build_merkle_tree(leaves)

        ab = hashlib.sha256(leaves[0] + leaves[1]).digest()
        cc = hashlib.sha256(leaves[2] + leaves[2]).digest()
        root = hashlib.sha256(ab + cc).digest()
        assert tree.root == root

    def test_empty_leaves_raises(self):
        """Test functionality: empty leaves raises."""
        with pytest.raises(BlockchainError):
            build_merkle_tree([])

    def test_levels_count(self):
        """Test functionality: levels count."""
        leaves = [_leaf(c) for c in "abcd"]
        tree = build_merkle_tree(leaves)
        # 4 leaves -> level0(4) -> level1(2) -> level2(1) = 3 levels
        assert len(tree.levels) == 3


# ---------------------------------------------------------------------------
# Merkle proof tests
# ---------------------------------------------------------------------------


class TestMerkleProof:
    """Tests for Merkle proof generation and verification."""

    @pytest.fixture()
    def four_leaf_tree(self):
        leaves = [_leaf(c) for c in "abcd"]
        return build_merkle_tree(leaves)

    def test_valid_proof_for_each_leaf(self, four_leaf_tree):
        """Test functionality: valid proof for each leaf."""
        tree = four_leaf_tree
        for i in range(len(tree.leaves)):
            proof_obj = get_merkle_proof(tree, i)
            assert verify_merkle_proof(proof_obj.leaf, proof_obj.proof, proof_obj.root)

    def test_tampered_leaf_fails_verification(self, four_leaf_tree):
        """Test functionality: tampered leaf fails verification."""
        tree = four_leaf_tree
        proof_obj = get_merkle_proof(tree, 0)
        tampered_leaf = b"\x00" * 32
        assert not verify_merkle_proof(tampered_leaf, proof_obj.proof, proof_obj.root)

    def test_tampered_root_fails_verification(self, four_leaf_tree):
        """Test functionality: tampered root fails verification."""
        tree = four_leaf_tree
        proof_obj = get_merkle_proof(tree, 0)
        tampered_root = b"\xff" * 32
        assert not verify_merkle_proof(proof_obj.leaf, proof_obj.proof, tampered_root)

    def test_out_of_range_index_raises(self, four_leaf_tree):
        """Test functionality: out of range index raises."""
        with pytest.raises(BlockchainError):
            get_merkle_proof(four_leaf_tree, 99)

    def test_proof_for_odd_tree(self):
        """Test functionality: proof for odd tree."""
        leaves = [_leaf(c) for c in "abc"]
        tree = build_merkle_tree(leaves)
        for i in range(3):
            proof_obj = get_merkle_proof(tree, i)
            assert verify_merkle_proof(proof_obj.leaf, proof_obj.proof, proof_obj.root)
