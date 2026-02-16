"""ERC-20 token interface and ABI encoding/decoding utilities.

Provides data structures representing ERC-20 tokens and transfer events,
along with helpers for ABI-encoding ``transfer(address, uint256)`` calls and
decoding transfer event log data.

Note:
    Uses SHA3-256 as a stand-in for Keccak-256. See ``addresses.py`` for
    details on this simplification.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from codomyrmex.crypto.exceptions import WalletError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def _sha3_256(data: bytes) -> bytes:
    """SHA3-256 hash (Keccak-256 educational stand-in)."""
    return hashlib.sha3_256(data).digest()


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ERC20Token:
    """Representation of an ERC-20 token's metadata.

    Attributes:
        name: Human-readable token name (e.g., ``"Tether USD"``).
        symbol: Ticker symbol (e.g., ``"USDT"``).
        decimals: Number of decimal places (typically 18).
        total_supply: Total supply in the smallest denomination.
    """

    name: str
    symbol: str
    decimals: int
    total_supply: int = 0


@dataclass
class TransferEvent:
    """Decoded ERC-20 ``Transfer`` event.

    Attributes:
        from_address: Sender address (hex, no ``0x`` prefix stored).
        to_address: Recipient address (hex, no ``0x`` prefix stored).
        value: Transfer amount in the smallest denomination.
    """

    from_address: str
    to_address: str
    value: int


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_erc20_interface(
    name: str,
    symbol: str,
    decimals: int = 18,
) -> ERC20Token:
    """Create an ERC-20 token interface descriptor.

    Args:
        name: Token name.
        symbol: Token ticker symbol.
        decimals: Number of decimal places (default 18).

    Returns:
        An ``ERC20Token`` instance with ``total_supply`` set to 0.

    Raises:
        WalletError: If decimals is negative.
    """
    if decimals < 0:
        raise WalletError("Token decimals must be non-negative")
    token = ERC20Token(name=name, symbol=symbol, decimals=decimals)
    logger.debug("Created ERC20 interface: %s (%s), decimals=%d", name, symbol, decimals)
    return token


# ---------------------------------------------------------------------------
# ABI encoding / decoding
# ---------------------------------------------------------------------------

# Function selector for transfer(address,uint256)
_TRANSFER_SELECTOR = _sha3_256(b"transfer(address,uint256)")[:4]

# Event topic for Transfer(address,address,uint256)
TRANSFER_EVENT_TOPIC = _sha3_256(b"Transfer(address,address,uint256)")


def encode_transfer(to: str, amount: int) -> bytes:
    """ABI-encode a ``transfer(address, uint256)`` function call.

    Layout (68 bytes total):
        - Bytes 0-3: function selector (first 4 bytes of hash of signature)
        - Bytes 4-35: ``to`` address left-padded to 32 bytes
        - Bytes 36-67: ``amount`` as a big-endian uint256 (32 bytes)

    Args:
        to: Recipient address as a hex string (with or without ``0x``
            prefix).
        amount: Token amount in the smallest denomination.

    Returns:
        68-byte ABI-encoded call data.

    Raises:
        WalletError: If encoding fails.
    """
    try:
        # Normalize address
        addr_hex = to.lower().replace("0x", "")
        if len(addr_hex) != 40:
            raise WalletError(f"Invalid address length: expected 40 hex chars, got {len(addr_hex)}")

        addr_bytes = bytes.fromhex(addr_hex)
        # Left-pad address to 32 bytes
        addr_padded = b"\x00" * 12 + addr_bytes

        # amount as uint256 (32 bytes, big-endian)
        if amount < 0:
            raise WalletError("Transfer amount must be non-negative")
        amount_padded = amount.to_bytes(32, "big")

        encoded = _TRANSFER_SELECTOR + addr_padded + amount_padded
        logger.debug(
            "Encoded transfer to=%s amount=%d (%d bytes)",
            to[:10],
            amount,
            len(encoded),
        )
        return encoded
    except WalletError:
        raise
    except Exception as exc:
        raise WalletError(f"Transfer encoding failed: {exc}") from exc


def decode_transfer_event(log_data: bytes) -> TransferEvent:
    """Decode an ABI-encoded ERC-20 Transfer event from log data.

    Expects the log data to contain three 32-byte words:
        - Word 0: ``from`` address (right-aligned in 32 bytes)
        - Word 1: ``to`` address (right-aligned in 32 bytes)
        - Word 2: ``value`` as uint256

    This corresponds to a non-indexed Transfer event or the concatenation
    of indexed topics with the data field, depending on the event encoding
    scheme used by the caller.

    Args:
        log_data: 96 bytes of ABI-encoded event data.

    Returns:
        A ``TransferEvent`` with decoded fields.

    Raises:
        WalletError: If the data length is incorrect or decoding fails.
    """
    if len(log_data) != 96:
        raise WalletError(
            f"Expected 96 bytes for Transfer event data, got {len(log_data)}"
        )

    try:
        from_addr = log_data[12:32].hex()
        to_addr = log_data[44:64].hex()
        value = int.from_bytes(log_data[64:96], "big")

        event = TransferEvent(from_address=from_addr, to_address=to_addr, value=value)
        logger.debug(
            "Decoded Transfer event: from=%s to=%s value=%d",
            from_addr[:10],
            to_addr[:10],
            value,
        )
        return event
    except WalletError:
        raise
    except Exception as exc:
        raise WalletError(f"Transfer event decoding failed: {exc}") from exc
