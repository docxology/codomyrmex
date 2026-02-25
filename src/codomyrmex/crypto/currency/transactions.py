"""Cryptocurrency transaction creation, signing, and verification.

Provides ECDSA-based transaction signing using the secp256k1 curve via the
``cryptography`` library. Transactions are serialized as canonical JSON for
deterministic hashing.

Note:
    This is an educational/reference implementation. Production transaction
    handling requires careful fee estimation, UTXO management, and replay
    protection.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils

from codomyrmex.crypto.exceptions import SignatureError, WalletError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class Transaction:
    """An unsigned cryptocurrency transaction.

    Attributes:
        sender: Sender address or identifier.
        recipient: Recipient address or identifier.
        amount: Transfer amount.
        timestamp: Unix timestamp of creation.
        tx_id: Transaction identifier (SHA-256 of canonical fields).
    """

    sender: str
    recipient: str
    amount: float
    timestamp: float
    tx_id: str = ""


@dataclass
class SignedTransaction:
    """A signed transaction bundled with the ECDSA signature and public key.

    Attributes:
        transaction: The underlying ``Transaction``.
        signature: DER-encoded ECDSA signature bytes.
        public_key: DER-encoded public key used for verification.
    """

    transaction: Transaction
    signature: bytes
    public_key: bytes


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def serialize_transaction(tx: Transaction) -> bytes:
    """Serialize a transaction to canonical JSON bytes.

    Fields are sorted to ensure deterministic output regardless of
    attribute ordering.

    Args:
        tx: The transaction to serialize.

    Returns:
        UTF-8 encoded JSON bytes.
    """
    payload = {
        "sender": tx.sender,
        "recipient": tx.recipient,
        "amount": tx.amount,
        "timestamp": tx.timestamp,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def deserialize_transaction(data: bytes) -> Transaction:
    """Deserialize JSON bytes back into a ``Transaction``.

    The ``tx_id`` is recomputed from the deserialized fields.

    Args:
        data: UTF-8 encoded JSON bytes (as produced by
            ``serialize_transaction``).

    Returns:
        A ``Transaction`` with a freshly computed ``tx_id``.

    Raises:
        WalletError: If deserialization fails.
    """
    try:
        payload = json.loads(data.decode("utf-8"))
        tx = Transaction(
            sender=payload["sender"],
            recipient=payload["recipient"],
            amount=payload["amount"],
            timestamp=payload["timestamp"],
        )
        tx.tx_id = hashlib.sha256(serialize_transaction(tx)).hexdigest()
        return tx
    except Exception as exc:
        raise WalletError(f"Transaction deserialization failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Creation
# ---------------------------------------------------------------------------


def create_transaction(sender: str, recipient: str, amount: float) -> Transaction:
    """Create a new unsigned transaction.

    Args:
        sender: Sender address.
        recipient: Recipient address.
        amount: Transfer amount (must be positive).

    Returns:
        A ``Transaction`` with a generated ``tx_id``.

    Raises:
        WalletError: If validation fails.
    """
    if amount <= 0:
        raise WalletError("Transaction amount must be positive")

    tx = Transaction(
        sender=sender,
        recipient=recipient,
        amount=amount,
        timestamp=time.time(),
    )
    tx.tx_id = hashlib.sha256(serialize_transaction(tx)).hexdigest()
    logger.debug("Created transaction %s: %s -> %s (%.8f)", tx.tx_id[:16], sender, recipient, amount)
    return tx


# ---------------------------------------------------------------------------
# Signing and verification
# ---------------------------------------------------------------------------


def sign_transaction(
    transaction: Transaction,
    private_key: ec.EllipticCurvePrivateKey,
) -> SignedTransaction:
    """Sign a transaction with an ECDSA private key (secp256k1).

    Args:
        transaction: The transaction to sign.
        private_key: A ``cryptography`` ECDSA private key on the secp256k1
            curve.

    Returns:
        A ``SignedTransaction`` containing the DER signature and public key.

    Raises:
        SignatureError: If signing fails.
    """
    try:
        tx_bytes = serialize_transaction(transaction)
        tx_hash = hashlib.sha256(tx_bytes).digest()

        signature = private_key.sign(
            tx_hash,
            ec.ECDSA(utils.Prehashed(hashes.SHA256())),
        )

        pub_bytes = private_key.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        logger.debug("Signed transaction %s", transaction.tx_id[:16])
        return SignedTransaction(
            transaction=transaction,
            signature=signature,
            public_key=pub_bytes,
        )
    except Exception as exc:
        if isinstance(exc, SignatureError):
            raise
        raise SignatureError(f"Transaction signing failed: {exc}") from exc


def verify_transaction(
    signed_tx: SignedTransaction,
    public_key: ec.EllipticCurvePublicKey | None = None,
) -> bool:
    """Verify the ECDSA signature on a signed transaction.

    Args:
        signed_tx: The signed transaction to verify.
        public_key: Optional explicit public key. If ``None`` the key
            embedded in the ``SignedTransaction`` is used.

    Returns:
        ``True`` if the signature is valid, ``False`` otherwise.
    """
    try:
        if public_key is None:
            public_key = serialization.load_der_public_key(signed_tx.public_key)

        tx_bytes = serialize_transaction(signed_tx.transaction)
        tx_hash = hashlib.sha256(tx_bytes).digest()

        public_key.verify(
            signed_tx.signature,
            tx_hash,
            ec.ECDSA(utils.Prehashed(hashes.SHA256())),
        )
        logger.debug("Transaction %s signature verified", signed_tx.transaction.tx_id[:16])
        return True
    except InvalidSignature:
        logger.debug("Transaction %s signature INVALID", signed_tx.transaction.tx_id[:16])
        return False
    except Exception as exc:
        logger.warning("Transaction verification error: %s", exc)
        return False
