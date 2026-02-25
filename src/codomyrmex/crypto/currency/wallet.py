"""HD wallet implementation following BIP-32 and BIP-39 standards.

Provides mnemonic generation, seed derivation, and hierarchical deterministic
wallet key derivation using the secp256k1 elliptic curve. Extended public and
private keys are serialized in the standard Base58Check format.

Note:
    This is an educational/reference implementation. Production wallets should
    use well-audited libraries and hardware security modules.
"""

from __future__ import annotations

import hashlib
import hmac
import struct

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from mnemonic import Mnemonic

from codomyrmex.crypto.encoding.base import encode_base58
from codomyrmex.crypto.exceptions import WalletError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# secp256k1 curve order
_SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def _hash160(data: bytes) -> bytes:
    """RIPEMD-160(SHA-256(data)) -- the standard Bitcoin Hash160."""
    sha = hashlib.sha256(data).digest()
    ripemd = hashlib.new("ripemd160", sha).digest()
    return ripemd


def _double_sha256(data: bytes) -> bytes:
    """Double SHA-256 hash used for Bitcoin checksums."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def _base58check_encode(payload: bytes) -> str:
    """Base58Check encoding: payload + 4-byte checksum."""
    checksum = _double_sha256(payload)[:4]
    return encode_base58(payload + checksum)


def _private_key_to_public(key_bytes: bytes) -> bytes:
    """Derive a compressed SEC1 public key (33 bytes) from raw private key bytes."""
    key_int = int.from_bytes(key_bytes, "big")
    if key_int == 0 or key_int >= _SECP256K1_ORDER:
        raise WalletError("Private key out of valid range for secp256k1")
    private_key_obj = ec.derive_private_key(key_int, ec.SECP256K1())
    public_key_obj = private_key_obj.public_key()
    return public_key_obj.public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.CompressedPoint,
    )


def _private_key_to_uncompressed_public(key_bytes: bytes) -> bytes:
    """Derive an uncompressed SEC1 public key (65 bytes) from raw private key bytes."""
    key_int = int.from_bytes(key_bytes, "big")
    if key_int == 0 or key_int >= _SECP256K1_ORDER:
        raise WalletError("Private key out of valid range for secp256k1")
    private_key_obj = ec.derive_private_key(key_int, ec.SECP256K1())
    public_key_obj = private_key_obj.public_key()
    return public_key_obj.public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.UncompressedPoint,
    )


# ---------------------------------------------------------------------------
# BIP-39 mnemonic helpers
# ---------------------------------------------------------------------------


def generate_mnemonic(strength: int = 256) -> str:
    """Generate a BIP-39 mnemonic phrase.

    Args:
        strength: Entropy bit length. 128 gives 12 words, 256 gives 24 words.

    Returns:
        Space-separated mnemonic word string.

    Raises:
        WalletError: If the strength value is invalid.
    """
    try:
        m = Mnemonic("english")
        mnemonic = m.generate(strength)
        logger.debug("Generated mnemonic with strength=%d", strength)
        return mnemonic
    except Exception as exc:
        raise WalletError(f"Mnemonic generation failed: {exc}") from exc


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """Derive a 64-byte seed from a BIP-39 mnemonic.

    Args:
        mnemonic: Space-separated mnemonic words.
        passphrase: Optional passphrase for additional entropy.

    Returns:
        64-byte seed suitable for HD wallet derivation.

    Raises:
        WalletError: If seed derivation fails.
    """
    try:
        seed = Mnemonic.to_seed(mnemonic, passphrase)
        logger.debug("Derived seed from mnemonic (passphrase=%s)", bool(passphrase))
        return seed
    except Exception as exc:
        raise WalletError(f"Seed derivation failed: {exc}") from exc


# ---------------------------------------------------------------------------
# BIP-32 HD wallet
# ---------------------------------------------------------------------------

# Extended key version bytes (mainnet)
_XPUB_VERSION = b"\x04\x88\xb2\x1e"  # 0x0488B21E
_XPRIV_VERSION = b"\x04\x88\xad\xe4"  # 0x0488ADE4


class HDWallet:
    """BIP-32 Hierarchical Deterministic Wallet.

    Supports master key derivation from a seed, child key derivation (both
    normal and hardened), address generation for Bitcoin and Ethereum, and
    extended key serialization.

    Attributes:
        private_key: 32-byte raw private key.
        chain_code: 32-byte chain code for child derivation.
        depth: Depth in the HD tree (0 for master).
        index: Child index (0 for master).
        parent_fingerprint: First 4 bytes of Hash160 of parent public key.
    """

    def __init__(self, seed: bytes) -> None:
        """Derive the BIP-32 master key from a seed.

        Args:
            seed: 64-byte seed (typically from ``mnemonic_to_seed``).

        Raises:
            WalletError: If the seed produces an invalid key.
        """
        if len(seed) < 16:
            raise WalletError("Seed must be at least 16 bytes")

        raw = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
        key = raw[:32]
        chain = raw[32:]

        key_int = int.from_bytes(key, "big")
        if key_int == 0 or key_int >= _SECP256K1_ORDER:
            raise WalletError("Derived master key is out of valid range")

        self.private_key: bytes = key
        self.chain_code: bytes = chain
        self.depth: int = 0
        self.index: int = 0
        self.parent_fingerprint: bytes = b"\x00\x00\x00\x00"

        logger.debug("HDWallet master key created (depth=0)")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _public_key(self) -> bytes:
        """Return the compressed public key (33 bytes) for this node."""
        return _private_key_to_public(self.private_key)

    def _fingerprint(self) -> bytes:
        """First 4 bytes of Hash160 of the compressed public key."""
        return _hash160(self._public_key())[:4]

    # ------------------------------------------------------------------
    # Child derivation
    # ------------------------------------------------------------------

    def derive_child(self, index: int) -> HDWallet:
        """Derive a child key using BIP-32 child key derivation.

        Args:
            index: Child index. Values >= 0x80000000 trigger hardened
                derivation.

        Returns:
            A new ``HDWallet`` representing the child node.

        Raises:
            WalletError: If derivation produces an invalid key.
        """
        hardened = index >= 0x80000000

        if hardened:
            # Hardened: HMAC-SHA512(chain_code, 0x00 || private_key || index)
            data = b"\x00" + self.private_key + struct.pack(">I", index)
        else:
            # Normal: HMAC-SHA512(chain_code, public_key || index)
            data = self._public_key() + struct.pack(">I", index)

        raw = hmac.new(self.chain_code, data, hashlib.sha512).digest()
        child_key_add = int.from_bytes(raw[:32], "big")
        child_chain = raw[32:]

        # child_key = (parent_key + child_key_add) mod n
        parent_int = int.from_bytes(self.private_key, "big")
        child_int = (parent_int + child_key_add) % _SECP256K1_ORDER

        if child_key_add >= _SECP256K1_ORDER or child_int == 0:
            raise WalletError(
                f"Child derivation at index {index} produced invalid key"
            )

        child = object.__new__(HDWallet)
        child.private_key = child_int.to_bytes(32, "big")
        child.chain_code = child_chain
        child.depth = self.depth + 1
        child.index = index
        child.parent_fingerprint = self._fingerprint()

        logger.debug(
            "Derived child key depth=%d index=%d hardened=%s",
            child.depth,
            index,
            hardened,
        )
        return child

    # ------------------------------------------------------------------
    # Address generation
    # ------------------------------------------------------------------

    def get_address(self, network: str = "bitcoin") -> str:
        """Generate a cryptocurrency address from this wallet key.

        Args:
            network: ``"bitcoin"`` for a P2PKH address or ``"ethereum"``
                for a checksummed Ethereum address.

        Returns:
            The address string.

        Raises:
            WalletError: If the network is unsupported.
        """
        if network == "bitcoin":
            pub = self._public_key()
            h160 = _hash160(pub)
            # Version byte 0x00 for mainnet
            payload = b"\x00" + h160
            return _base58check_encode(payload)

        if network == "ethereum":
            # Ethereum uses the Keccak-256 of the uncompressed public key
            # (without the 0x04 prefix).  We use SHA3-256 as a simplified
            # stand-in; see addresses.py for the full note.
            pub_uncompressed = _private_key_to_uncompressed_public(self.private_key)
            # Strip the 0x04 prefix
            pub_body = pub_uncompressed[1:]
            addr_hash = hashlib.sha3_256(pub_body).digest()
            raw_addr = addr_hash[-20:]
            hex_addr = raw_addr.hex()
            # EIP-55 checksum
            hash_hex = hashlib.sha3_256(hex_addr.encode("ascii")).hexdigest()
            checksummed = "".join(
                c.upper() if int(hash_hex[i], 16) >= 8 else c
                for i, c in enumerate(hex_addr)
            )
            return "0x" + checksummed

        raise WalletError(f"Unsupported network: {network}")

    # ------------------------------------------------------------------
    # Extended key serialization
    # ------------------------------------------------------------------

    def export_xpub(self) -> str:
        """Serialize the extended public key in Base58Check format.

        Returns:
            The ``xpub...`` string.
        """
        payload = (
            _XPUB_VERSION
            + struct.pack("B", self.depth)
            + self.parent_fingerprint
            + struct.pack(">I", self.index)
            + self.chain_code
            + self._public_key()
        )
        return _base58check_encode(payload)

    def export_xpriv(self) -> str:
        """Serialize the extended private key in Base58Check format.

        Returns:
            The ``xprv...`` string.
        """
        payload = (
            _XPRIV_VERSION
            + struct.pack("B", self.depth)
            + self.parent_fingerprint
            + struct.pack(">I", self.index)
            + self.chain_code
            + b"\x00"
            + self.private_key
        )
        return _base58check_encode(payload)


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------


def create_hd_wallet(mnemonic: str | None = None) -> HDWallet:
    """Create an HD wallet, optionally generating a new mnemonic.

    Args:
        mnemonic: BIP-39 mnemonic. If ``None`` a new 24-word mnemonic is
            generated.

    Returns:
        An ``HDWallet`` instance at the master (root) level.

    Raises:
        WalletError: If wallet creation fails.
    """
    if mnemonic is None:
        mnemonic = generate_mnemonic(256)
        logger.info("Generated new 24-word mnemonic for HD wallet")
    seed = mnemonic_to_seed(mnemonic)
    return HDWallet(seed)
