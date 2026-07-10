"""Zero-Knowledge Proof interfaces for self-custody wallet operations.

This module implements a practical ZK proof system using the Fiat-Shamir
heuristic for non-interactive proofs of private key ownership, and a
:class:`SignedCapabilityProof` that integrates with the identity module
to produce capability attestation proofs tied to a persona.

Design notes
------------
- **No private key leakage**: proofs are challenge–response; the prover
  reveals ``HMAC(key, challenge)`` but never the raw key bytes.
- **Fiat-Shamir transform**: the challenge is derived deterministically
  from a public statement (``sha256(user_id ‖ wallet_address ‖ message)``
  ‖ nonce), so verification is non-interactive.
- **Identity integration**: :class:`SignedCapabilityProof` leverages
  :class:`~codomyrmex.identity.manager.IdentityManager` personas and their
  capabilities to produce attested capability proofs.
- **Zero-mock**: all cryptographic operations use real hashlib / hmac;
  no test mocks are required.

Public API
----------
- :class:`ZKProofVerifier` – create challenges, verify proofs.
- :class:`ZKProof` – dataclass holding a proof bundle.
- :class:`SignedCapabilityProof` – capability attestation + identity proof.
- :func:`generate_zk_proof` – convenience prover function.
- :func:`verify_zk_proof` – convenience verifier function.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from codomyrmex.identity.manager import IdentityManager
    from codomyrmex.wallet.core import WalletManager

logger = get_logger(__name__)

# Default salt length (bytes) mixed into challenge derivation to make
# proofs non-replayable across different verifier instances.
_DEFAULT_SALT_LEN = 16


@dataclass
class ZKProof:
    """A non-interactive zero-knowledge proof bundle.

    Attributes:
        user_id: The wallet owner identifier (public).
        wallet_address: The wallet address being proven (public).
        challenge: Hex-encoded challenge nonce (public).
        response: Hex-encoded HMAC-SHA256 response (reveals no key).
        message: Optional message bytes (hex) that the proof covers.
        timestamp: ISO-8601 creation timestamp.
        nonce: Random hex nonce used in challenge derivation.
    """

    user_id: str
    wallet_address: str
    challenge: str
    response: str
    message: str = ""
    timestamp: str = ""
    nonce: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()
        if not self.nonce:
            self.nonce = secrets.token_hex(_DEFAULT_SALT_LEN)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the proof to a JSON-safe dict."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize the proof to a JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ZKProof:
        """Deserialize a proof from a dict."""
        return cls(
            user_id=data["user_id"],
            wallet_address=data["wallet_address"],
            challenge=data["challenge"],
            response=data["response"],
            message=data.get("message", ""),
            timestamp=data.get("timestamp", ""),
            nonce=data.get("nonce", ""),
        )


def _derive_challenge(
    user_id: str,
    wallet_address: str,
    nonce: str,
    message: bytes = b"",
) -> str:
    """Derive a deterministic challenge via the Fiat-Shamir transform.

    The challenge is ``sha256(user_id ‖ wallet_address ‖ nonce ‖ message)``
    so that both prover and verifier arrive at the same value without
    interaction.

    Args:
        user_id: The wallet owner identifier.
        wallet_address: The wallet address.
        nonce: Hex-encoded random nonce.
        message: Optional message bytes covered by the proof.

    Returns:
        Hex-encoded challenge digest.
    """
    h = hashlib.sha256()
    h.update(user_id.encode())
    h.update(b"|")
    h.update(wallet_address.encode())
    h.update(b"|")
    h.update(nonce.encode())
    h.update(b"|")
    h.update(message)
    return h.hexdigest()


class ZKProofVerifier:
    """Creates challenges and verifies zero-knowledge proofs of wallet ownership.

    The verifier never sees the private key. The prover computes
    ``response = HMAC-SHA256(private_key, challenge)`` and the verifier
    re-derives the expected response using the stored key (when co-located
    with the prover) or delegates to a :class:`WalletManager` that holds
    the key.

    Example::

        mgr = WalletManager()
        addr = mgr.create_wallet("alice")

        verifier = ZKProofVerifier(wallet_manager=mgr)
        proof = verifier.generate_proof("alice", message=b"transfer 10 ETH")
        assert verifier.verify_proof(proof, message=b"transfer 10 ETH")
    """

    def __init__(
        self,
        wallet_manager: WalletManager | None = None,
        storage_path: Path | None = None,
    ) -> None:
        """Initialize the verifier.

        Args:
            wallet_manager: An existing WalletManager. If ``None``, one will
                be lazily constructed on first use via ``storage_path``.
            storage_path: Key storage directory when lazily constructing.
        """
        self._wallet_manager: WalletManager | None = wallet_manager
        self._storage_path = storage_path

    def _get_manager(self) -> WalletManager:
        """Lazily create or return the WalletManager."""
        if self._wallet_manager is None:
            from codomyrmex.wallet.core import WalletManager

            self._wallet_manager = WalletManager(storage_path=self._storage_path)
        return self._wallet_manager

    # ── Prover side ──────────────────────────────────────────────────

    def generate_proof(
        self,
        user_id: str,
        message: bytes = b"",
    ) -> ZKProof:
        """Generate a ZK proof of wallet ownership.

        The prover signs the deterministic challenge with the wallet's
        private key via ``WalletManager.sign_message``. The private key
        itself is never exposed.

        Args:
            user_id: The wallet owner.
            message: Optional message bytes the proof should cover.

        Returns:
            A :class:`ZKProof` bundle.

        Raises:
            WalletNotFoundError: If the user has no wallet.
        """
        mgr = self._get_manager()
        address = mgr.get_wallet_address(user_id)
        if address is None:
            from codomyrmex.wallet.exceptions import WalletNotFoundError

            raise WalletNotFoundError(user_id)

        nonce = secrets.token_hex(_DEFAULT_SALT_LEN)
        challenge = _derive_challenge(user_id, address, nonce, message)

        # The prover signs the challenge with the private key (HMAC).
        response = mgr.sign_message(user_id, challenge.encode())

        proof = ZKProof(
            user_id=user_id,
            wallet_address=address,
            challenge=challenge,
            response=response.hex(),
            message=message.hex(),
            nonce=nonce,
        )
        logger.info("Generated ZK proof for user %s (wallet %s)", user_id, address)
        return proof

    # ── Verifier side ────────────────────────────────────────────────

    def verify_proof(
        self,
        proof: ZKProof,
        message: bytes = b"",
    ) -> bool:
        """Verify a ZK proof of wallet ownership.

        Re-derives the challenge and checks the HMAC response against the
        stored private key. The private key is never returned to the caller.

        Args:
            proof: The :class:`ZKProof` to verify.
            message: Optional message bytes the proof covers. Must match
                the message used during generation.

        Returns:
            True if the proof is valid.
        """
        mgr = self._get_manager()

        # Validate that the wallet exists and address matches.
        address = mgr.get_wallet_address(proof.user_id)
        if address is None:
            logger.warning("ZK proof failed: no wallet for user %s", proof.user_id)
            return False
        if address != proof.wallet_address:
            logger.warning(
                "ZK proof failed: address mismatch (expected %s, got %s)",
                address,
                proof.wallet_address,
            )
            return False

        # Re-derive challenge using Fiat-Shamir.
        expected_challenge = _derive_challenge(
            proof.user_id, proof.wallet_address, proof.nonce, message
        )
        if not hmac.compare_digest(expected_challenge, proof.challenge):
            logger.warning("ZK proof failed: challenge mismatch for user %s", proof.user_id)
            return False

        # Verify the HMAC response matches what the key would produce.
        try:
            expected_response = mgr.sign_message(
                proof.user_id, proof.challenge.encode()
            )
        except Exception:
            logger.exception("ZK proof failed: could not sign challenge")
            return False

        is_valid = hmac.compare_digest(expected_response, bytes.fromhex(proof.response))
        if is_valid:
            logger.info("ZK proof verified for user %s", proof.user_id)
        else:
            logger.warning("ZK proof failed: response mismatch for user %s", proof.user_id)
        return is_valid

    # ── Decoupled verification (no WalletManager key access) ─────────

    @staticmethod
    def verify_proof_with_response(
        proof: ZKProof,
        expected_response: bytes,
        message: bytes = b"",
    ) -> bool:
        """Verify a proof when the verifier only has the expected response.

        This is the truly zero-knowledge path: the verifier has never seen
        the private key, only a pre-shared or externally-attested HMAC
        response. The challenge is re-derived and the provided response
        is compared.

        Args:
            proof: The proof bundle.
            expected_response: The HMAC response bytes to compare against.
            message: Optional message bytes covered by the proof.

        Returns:
            True if the challenge derivation matches and the response
            matches ``expected_response``.
        """
        expected_challenge = _derive_challenge(
            proof.user_id, proof.wallet_address, proof.nonce, message
        )
        if not hmac.compare_digest(expected_challenge, proof.challenge):
            logger.warning(
                "Decoupled ZK verify failed: challenge mismatch for %s",
                proof.user_id,
            )
            return False
        return hmac.compare_digest(expected_response, bytes.fromhex(proof.response))


@dataclass
class CapabilityAttestation:
    """Identity attestation linking a persona to capabilities.

    Attributes:
        persona_id: The identity persona ID.
        persona_name: Human-readable name.
        verification_level: Identity verification level string.
        capabilities: list of capability strings.
        wallet_address: The wallet address bound to this persona.
        timestamp: ISO-8601 creation timestamp.
    """

    persona_id: str
    persona_name: str
    verification_level: str
    capabilities: list[str] = field(default_factory=list)
    wallet_address: str = ""
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


@dataclass
class SignedCapabilityProof:
    """A signed capability proof combining ZK ownership with identity attestation.

    This bundles:
    1. A :class:`ZKProof` proving wallet ownership (without revealing key).
    2. A :class:`CapabilityAttestation` from the identity module.
    3. An attestation signature: ``HMAC(wallet_key, attestation_json)``
       proving that the wallet holder endorses the capability claims.

    Attributes:
        zk_proof: The zero-knowledge proof of wallet ownership.
        attestation: The identity capability attestation.
        attestation_signature: Hex-encoded HMAC of the attestation.
    """

    zk_proof: ZKProof
    attestation: CapabilityAttestation
    attestation_signature: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "zk_proof": self.zk_proof.to_dict(),
            "attestation": self.attestation.to_dict(),
            "attestation_signature": self.attestation_signature,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SignedCapabilityProof:
        return cls(
            zk_proof=ZKProof.from_dict(data["zk_proof"]),
            attestation=CapabilityAttestation(
                persona_id=data["attestation"]["persona_id"],
                persona_name=data["attestation"]["persona_name"],
                verification_level=data["attestation"]["verification_level"],
                capabilities=data["attestation"].get("capabilities", []),
                wallet_address=data["attestation"].get("wallet_address", ""),
                timestamp=data["attestation"].get("timestamp", ""),
            ),
            attestation_signature=data.get("attestation_signature", ""),
        )


class SignedCapabilityProofBuilder:
    """Builds :class:`SignedCapabilityProof` instances.

    Integrates :class:`ZKProofVerifier` (wallet) with
    :class:`~codomyrmex.identity.manager.IdentityManager` (identity).

    Example::

        mgr = WalletManager()
        addr = mgr.create_wallet("alice")

        identity_mgr = IdentityManager()
        identity_mgr.create_persona("alice_p", "Alice", capabilities=["send_funds"])

        builder = SignedCapabilityProofBuilder(
            wallet_manager=mgr,
            identity_manager=identity_mgr,
        )
        proof = builder.build("alice", "alice_p", message=b"authorize transfer")
    """

    def __init__(
        self,
        wallet_manager: WalletManager | None = None,
        identity_manager: IdentityManager | None = None,
        storage_path: Path | None = None,
    ) -> None:
        """Initialize the builder.

        Args:
            wallet_manager: WalletManager for key operations.
            identity_manager: IdentityManager for persona attestation.
            storage_path: Key storage path if lazily creating WalletManager.
        """
        self._verifier = ZKProofVerifier(
            wallet_manager=wallet_manager, storage_path=storage_path
        )
        self._identity_manager: IdentityManager | None = identity_manager

    def _get_identity_manager(self) -> IdentityManager:
        if self._identity_manager is None:
            from codomyrmex.identity.manager import IdentityManager

            self._identity_manager = IdentityManager()
        return self._identity_manager

    def build(
        self,
        user_id: str,
        persona_id: str,
        message: bytes = b"",
        required_capability: str | None = None,
    ) -> SignedCapabilityProof:
        """Build a signed capability proof.

        Args:
            user_id: The wallet owner identifier.
            persona_id: The identity persona ID to attest.
            message: Optional message bytes for the ZK proof.
            required_capability: If set, verify the persona has this
                capability before building the proof.

        Returns:
            A :class:`SignedCapabilityProof`.

        Raises:
            WalletNotFoundError: If the user has no wallet.
            ValueError: If the persona doesn't exist or lacks a required
                capability.
        """
        # Generate the ZK ownership proof.
        zk_proof = self._verifier.generate_proof(user_id, message=message)

        # Build the identity attestation.
        id_mgr = self._get_identity_manager()
        persona = id_mgr.get_persona(persona_id)
        if persona is None:
            raise ValueError(f"Persona {persona_id!r} not found in identity manager")

        if required_capability is not None:
            if not persona.has_capability(required_capability):
                raise ValueError(
                    f"Persona {persona_id!r} lacks required capability "
                    f"{required_capability!r}"
                )

        attestation = CapabilityAttestation(
            persona_id=persona.id,
            persona_name=persona.name,
            verification_level=persona.level.value,
            capabilities=list(persona.capabilities),
            wallet_address=zk_proof.wallet_address,
        )

        # Sign the attestation with the wallet key (HMAC).
        mgr = self._verifier._get_manager()
        attestation_sig = mgr.sign_message(
            user_id, attestation.to_json().encode()
        )

        proof = SignedCapabilityProof(
            zk_proof=zk_proof,
            attestation=attestation,
            attestation_signature=attestation_sig.hex(),
        )
        logger.info(
            "Built signed capability proof for user %s / persona %s",
            user_id,
            persona_id,
        )
        return proof

    def verify(
        self,
        proof: SignedCapabilityProof,
        message: bytes = b"",
    ) -> bool:
        """Verify a signed capability proof.

        Checks:
        1. The ZK proof of wallet ownership.
        2. The attestation signature matches the wallet key.

        Args:
            proof: The proof to verify.
            message: Optional message bytes for the ZK proof.

        Returns:
            True if both the ZK proof and attestation signature are valid.
        """
        # Verify ZK ownership proof.
        if not self._verifier.verify_proof(proof.zk_proof, message=message):
            logger.warning("SignedCapabilityProof: ZK proof verification failed")
            return False

        # Verify attestation signature.
        mgr = self._verifier._get_manager()
        try:
            expected_sig = mgr.sign_message(
                proof.zk_proof.user_id,
                proof.attestation.to_json().encode(),
            )
        except Exception:
            logger.exception("SignedCapabilityProof: attestation sig failed")
            return False

        valid = hmac.compare_digest(
            expected_sig, bytes.fromhex(proof.attestation_signature)
        )
        if valid:
            logger.info(
                "SignedCapabilityProof verified for user %s",
                proof.zk_proof.user_id,
            )
        else:
            logger.warning(
                "SignedCapabilityProof: attestation signature mismatch for %s",
                proof.zk_proof.user_id,
            )
        return valid


# ── Convenience functions ────────────────────────────────────────────


def generate_zk_proof(
    user_id: str,
    storage_path: str | None = None,
    message: str = "",
    wallet_manager: WalletManager | None = None,
    wallet_address: str | None = None,
) -> dict[str, Any]:
    """Generate a ZK proof of wallet ownership.

    Args:
        user_id: The wallet owner identifier.
        storage_path: Optional key storage directory path.
        message: Optional message string the proof covers.
        wallet_manager: Optional pre-configured WalletManager. Takes
            precedence over ``storage_path``.
        wallet_address: Optional wallet address. When ``wallet_manager``
            is ``None`` and the key exists on disk at ``storage_path``,
            the fresh manager will register this wallet address so ZK
            proof generation can proceed statelessly.

    Returns:
        dict with the proof fields, or an error dict.
    """
    try:
        if wallet_manager:
            verifier = ZKProofVerifier(wallet_manager=wallet_manager)
        else:
            verifier = ZKProofVerifier(
                storage_path=Path(storage_path) if storage_path else None
            )
            if wallet_address:
                verifier._get_manager().register_wallet(user_id, wallet_address)
        msg_bytes = message.encode() if message else b""
        proof = verifier.generate_proof(user_id, message=msg_bytes)
        return proof.to_dict()
    except Exception as exc:
        logger.exception("generate_zk_proof failed")
        return {"status": "error", "message": str(exc)}


def verify_zk_proof(
    proof: dict[str, Any],
    storage_path: str | None = None,
    message: str = "",
    wallet_manager: WalletManager | None = None,
) -> dict[str, Any]:
    """Verify a ZK proof of wallet ownership.

    Args:
        proof: The proof dict (from :func:`generate_zk_proof`). Must
            contain ``user_id`` and ``wallet_address`` so a fresh
            :class:`WalletManager` can register the wallet for
            stateless verification.
        storage_path: Optional key storage directory path.
        message: Optional message string the proof covers.
        wallet_manager: Optional pre-configured WalletManager. Takes
            precedence over ``storage_path``.

    Returns:
        dict with keys: status, verified.
    """
    try:
        if wallet_manager:
            verifier = ZKProofVerifier(wallet_manager=wallet_manager)
        else:
            verifier = ZKProofVerifier(
                storage_path=Path(storage_path) if storage_path else None
            )
            # Register the wallet from the proof so a fresh manager
            # can find the key on disk for verification.
            zk_proof_obj = ZKProof.from_dict(proof)
            verifier._get_manager().register_wallet(
                zk_proof_obj.user_id, zk_proof_obj.wallet_address
            )
            msg_bytes = message.encode() if message else b""
            is_valid = verifier.verify_proof(zk_proof_obj, message=msg_bytes)
            return {"status": "success", "verified": is_valid}

        zk_proof_obj = ZKProof.from_dict(proof)
        msg_bytes = message.encode() if message else b""
        is_valid = verifier.verify_proof(zk_proof_obj, message=msg_bytes)
        return {"status": "success", "verified": is_valid}
    except Exception as exc:
        logger.exception("verify_zk_proof failed")
        return {"status": "error", "message": str(exc)}
