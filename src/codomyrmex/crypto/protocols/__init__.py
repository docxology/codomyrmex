"""Cryptographic protocols: key exchange, secret sharing, zero-knowledge proofs.

Public API re-exports for convenient access to protocol primitives.
"""

from __future__ import annotations

from codomyrmex.crypto.protocols.key_exchange import (
    DHKeyPair,
    ECDHKeyPair,
    dh_compute_shared_secret,
    dh_generate_keypair,
    dh_generate_parameters,
    ecdh_compute_shared_secret,
    ecdh_generate_keypair,
)
from codomyrmex.crypto.protocols.secret_sharing import (
    PRIME,
    Share,
    generate_share_commitment,
    reconstruct_secret,
    split_secret,
    verify_share,
)
from codomyrmex.crypto.protocols.zero_knowledge import (
    SchnorrProof,
    pedersen_commit,
    pedersen_verify,
    schnorr_prove,
    schnorr_verify,
)

__all__ = [
    # Secret sharing
    "PRIME",
    # Key exchange
    "DHKeyPair",
    "ECDHKeyPair",
    # Zero knowledge
    "SchnorrProof",
    "Share",
    "dh_compute_shared_secret",
    "dh_generate_keypair",
    "dh_generate_parameters",
    "ecdh_compute_shared_secret",
    "ecdh_generate_keypair",
    "generate_share_commitment",
    "pedersen_commit",
    "pedersen_verify",
    "reconstruct_secret",
    "schnorr_prove",
    "schnorr_verify",
    "split_secret",
    "verify_share",
]
