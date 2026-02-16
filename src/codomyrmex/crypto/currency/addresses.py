"""Cryptocurrency address generation and validation.

Supports Bitcoin P2PKH addresses (mainnet and testnet) and Ethereum
checksummed addresses (EIP-55).

Note:
    Ethereum address derivation requires Keccak-256, which differs from the
    NIST SHA3-256 standard. This implementation uses ``hashlib.sha3_256`` as
    an educational stand-in. For production Ethereum tooling, use a proper
    Keccak-256 implementation (e.g., ``pysha3`` or ``pycryptodome``).
"""

from __future__ import annotations

import hashlib
import re

from codomyrmex.crypto.encoding.base import encode_base58, decode_base58
from codomyrmex.crypto.exceptions import WalletError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Bitcoin version bytes
_MAINNET_VERSION = b"\x00"
_TESTNET_VERSION = b"\x6f"


def _double_sha256(data: bytes) -> bytes:
    """Double SHA-256 hash."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def _hash160(data: bytes) -> bytes:
    """RIPEMD-160(SHA-256(data))."""
    sha = hashlib.sha256(data).digest()
    return hashlib.new("ripemd160", sha).digest()


def _sha3_256(data: bytes) -> bytes:
    """SHA3-256 hash (used as Keccak-256 stand-in for educational purposes)."""
    return hashlib.sha3_256(data).digest()


# ---------------------------------------------------------------------------
# Bitcoin
# ---------------------------------------------------------------------------


def generate_bitcoin_address(
    public_key: bytes,
    network: str = "mainnet",
) -> str:
    """Generate a Bitcoin P2PKH address from a public key.

    Steps:
        1. SHA-256 of public key
        2. RIPEMD-160 of that (Hash160)
        3. Prepend version byte (0x00 mainnet, 0x6f testnet)
        4. Double-SHA-256 checksum (first 4 bytes)
        5. Base58 encode (version + hash160 + checksum)

    Args:
        public_key: Compressed (33 bytes) or uncompressed (65 bytes) SEC1
            public key.
        network: ``"mainnet"`` or ``"testnet"``.

    Returns:
        Base58Check-encoded Bitcoin address.

    Raises:
        WalletError: If the network is unknown.
    """
    if network == "mainnet":
        version = _MAINNET_VERSION
    elif network == "testnet":
        version = _TESTNET_VERSION
    else:
        raise WalletError(f"Unknown Bitcoin network: {network}")

    h160 = _hash160(public_key)
    payload = version + h160
    checksum = _double_sha256(payload)[:4]
    address = encode_base58(payload + checksum)

    logger.debug("Generated Bitcoin %s address: %s", network, address)
    return address


def validate_bitcoin_address(address: str) -> bool:
    """Validate a Bitcoin address by verifying its Base58Check checksum.

    Args:
        address: A Base58Check-encoded Bitcoin address.

    Returns:
        ``True`` if the checksum is valid, ``False`` otherwise.
    """
    try:
        decoded = decode_base58(address)
        if len(decoded) != 25:
            return False
        payload = decoded[:-4]
        checksum = decoded[-4:]
        expected = _double_sha256(payload)[:4]
        valid = checksum == expected
        logger.debug("Bitcoin address %s validation: %s", address[:8], valid)
        return valid
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Ethereum
# ---------------------------------------------------------------------------


def checksum_ethereum_address(address: str) -> str:
    """Apply EIP-55 mixed-case checksum encoding to an Ethereum address.

    Args:
        address: A 40-character hex string (with or without ``0x`` prefix).

    Returns:
        The ``0x``-prefixed checksummed address.

    Raises:
        WalletError: If the address format is invalid.
    """
    # Normalize: strip 0x, lowercase
    hex_addr = address.lower().replace("0x", "")
    if len(hex_addr) != 40 or not re.fullmatch(r"[0-9a-f]{40}", hex_addr):
        raise WalletError(f"Invalid Ethereum address hex: {address}")

    addr_hash = _sha3_256(hex_addr.encode("ascii")).hex()

    checksummed = ""
    for i, c in enumerate(hex_addr):
        if c in "0123456789":
            checksummed += c
        elif int(addr_hash[i], 16) >= 8:
            checksummed += c.upper()
        else:
            checksummed += c.lower()

    return "0x" + checksummed


def generate_ethereum_address(public_key: bytes) -> str:
    """Generate an EIP-55 checksummed Ethereum address from a public key.

    For 65-byte uncompressed keys (``04`` prefix), the first byte is
    stripped before hashing. The last 20 bytes of the SHA3-256 hash
    (Keccak-256 stand-in) form the raw address.

    Args:
        public_key: Uncompressed (65 bytes) or stripped (64 bytes) public
            key.

    Returns:
        ``0x``-prefixed EIP-55 checksummed address.

    Raises:
        WalletError: If the public key format is invalid.
    """
    if len(public_key) == 65 and public_key[0] == 0x04:
        pub_body = public_key[1:]
    elif len(public_key) == 64:
        pub_body = public_key
    else:
        raise WalletError(
            f"Expected 64 or 65 byte public key, got {len(public_key)} bytes"
        )

    addr_hash = _sha3_256(pub_body)
    raw_addr = addr_hash[-20:]
    hex_addr = raw_addr.hex()

    address = checksum_ethereum_address(hex_addr)
    logger.debug("Generated Ethereum address: %s", address)
    return address


def validate_ethereum_address(address: str) -> bool:
    """Validate an Ethereum address format and optional EIP-55 checksum.

    Checks:
        1. Must start with ``0x``.
        2. Must be followed by exactly 40 hex characters.
        3. If mixed-case, must match EIP-55 checksum.

    Args:
        address: The address to validate.

    Returns:
        ``True`` if valid, ``False`` otherwise.
    """
    if not address.startswith("0x"):
        return False

    hex_part = address[2:]
    if len(hex_part) != 40:
        return False

    if not re.fullmatch(r"[0-9a-fA-F]{40}", hex_part):
        return False

    # If all lowercase or all uppercase, format is valid (no checksum to verify)
    if hex_part == hex_part.lower() or hex_part == hex_part.upper():
        return True

    # Mixed case -- verify EIP-55 checksum
    try:
        expected = checksum_ethereum_address(hex_part)
        valid = address == expected
        logger.debug("Ethereum address EIP-55 validation: %s", valid)
        return valid
    except Exception:
        return False
