"""Unit tests for codomyrmex.crypto.currency.transactions."""

from __future__ import annotations

import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from codomyrmex.crypto.currency.transactions import (
    Transaction,
    create_transaction,
    sign_transaction,
    verify_transaction,
    serialize_transaction,
    deserialize_transaction,
)
from codomyrmex.crypto.exceptions import WalletError


pytestmark = [pytest.mark.crypto, pytest.mark.unit]


@pytest.fixture()
def keypair():
    """Generate a fresh secp256k1 key pair."""
    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key()
    return private_key, public_key


# ---------------------------------------------------------------------------
# Transaction creation
# ---------------------------------------------------------------------------


class TestCreateTransaction:
    """Tests for transaction creation."""

    def test_creates_with_tx_id(self):
        """Test functionality: creates with tx id."""
        tx = create_transaction("alice", "bob", 1.5)
        assert tx.tx_id
        assert len(tx.tx_id) == 64  # SHA-256 hex

    def test_fields_match(self):
        """Test functionality: fields match."""
        tx = create_transaction("alice", "bob", 3.14)
        assert tx.sender == "alice"
        assert tx.recipient == "bob"
        assert tx.amount == 3.14

    def test_timestamp_set(self):
        """Test functionality: timestamp set."""
        tx = create_transaction("a", "b", 1.0)
        assert tx.timestamp > 0

    def test_zero_amount_raises(self):
        """Test functionality: zero amount raises."""
        with pytest.raises(WalletError):
            create_transaction("a", "b", 0)

    def test_negative_amount_raises(self):
        """Test functionality: negative amount raises."""
        with pytest.raises(WalletError):
            create_transaction("a", "b", -5)


# ---------------------------------------------------------------------------
# Serialization roundtrip
# ---------------------------------------------------------------------------


class TestSerialization:
    """Tests for transaction serialization and deserialization."""

    def test_roundtrip_preserves_fields(self):
        """Test functionality: roundtrip preserves fields."""
        tx = create_transaction("alice", "bob", 42.0)
        data = serialize_transaction(tx)
        restored = deserialize_transaction(data)
        assert restored.sender == tx.sender
        assert restored.recipient == tx.recipient
        assert restored.amount == tx.amount
        assert restored.timestamp == tx.timestamp

    def test_roundtrip_tx_id_matches(self):
        """Test functionality: roundtrip tx id matches."""
        tx = create_transaction("alice", "bob", 42.0)
        data = serialize_transaction(tx)
        restored = deserialize_transaction(data)
        assert restored.tx_id == tx.tx_id

    def test_serialized_is_bytes(self):
        """Test functionality: serialized is bytes."""
        tx = create_transaction("a", "b", 1.0)
        assert isinstance(serialize_transaction(tx), bytes)

    def test_invalid_bytes_raises(self):
        """Test functionality: invalid bytes raises."""
        with pytest.raises(WalletError):
            deserialize_transaction(b"not-valid-json")


# ---------------------------------------------------------------------------
# Signing and verification
# ---------------------------------------------------------------------------


class TestSignAndVerify:
    """Tests for ECDSA transaction signing and verification."""

    def test_sign_produces_signature(self, keypair):
        """Test functionality: sign produces signature."""
        private_key, _ = keypair
        tx = create_transaction("alice", "bob", 10.0)
        signed = sign_transaction(tx, private_key)
        assert signed.signature
        assert len(signed.signature) > 0
        assert signed.public_key

    def test_verify_valid_signature(self, keypair):
        """Test functionality: verify valid signature."""
        private_key, public_key = keypair
        tx = create_transaction("alice", "bob", 10.0)
        signed = sign_transaction(tx, private_key)
        assert verify_transaction(signed, public_key) is True

    def test_verify_with_embedded_key(self, keypair):
        """Test functionality: verify with embedded key."""
        private_key, _ = keypair
        tx = create_transaction("alice", "bob", 10.0)
        signed = sign_transaction(tx, private_key)
        # Let verify_transaction use the embedded public_key bytes
        assert verify_transaction(signed) is True

    def test_tampered_amount_fails(self, keypair):
        """Test functionality: tampered amount fails."""
        private_key, public_key = keypair
        tx = create_transaction("alice", "bob", 10.0)
        signed = sign_transaction(tx, private_key)
        # Tamper with the transaction
        signed.transaction.amount = 999.0
        assert verify_transaction(signed, public_key) is False

    def test_tampered_recipient_fails(self, keypair):
        """Test functionality: tampered recipient fails."""
        private_key, public_key = keypair
        tx = create_transaction("alice", "bob", 10.0)
        signed = sign_transaction(tx, private_key)
        signed.transaction.recipient = "eve"
        assert verify_transaction(signed, public_key) is False

    def test_wrong_key_fails(self, keypair):
        """Test functionality: wrong key fails."""
        private_key, _ = keypair
        other_private = ec.generate_private_key(ec.SECP256K1())
        other_public = other_private.public_key()
        tx = create_transaction("alice", "bob", 10.0)
        signed = sign_transaction(tx, private_key)
        assert verify_transaction(signed, other_public) is False
