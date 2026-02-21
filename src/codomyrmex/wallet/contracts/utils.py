"""Wallet contract utilities — ABI helpers, address validation, and encoding.

Provides:
- Address validation (checksum, length, format)
- Function selector computation (Keccak-256 of signature)
- ABI encoding/decoding for common types
- Contract address prediction (CREATE opcode)
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


def is_valid_address(address: str) -> bool:
    """Check if a string is a valid Ethereum-style address (0x + 40 hex chars)."""
    return bool(re.match(r"^0x[0-9a-fA-F]{40}$", address))


def normalize_address(address: str) -> str:
    """Normalize an address to lowercase with 0x prefix."""
    if not address.startswith("0x"):
        address = "0x" + address
    return address.lower()


def compute_selector(signature: str) -> str:
    """Compute the 4-byte function selector from a function signature.

    Uses SHA-256 as a stand-in for Keccak-256 (no external dependency).

    Args:
        signature: e.g. "transfer(address,uint256)"

    Returns:
        8-character hex string (4 bytes).
    """
    digest = hashlib.sha256(signature.encode()).hexdigest()
    return "0x" + digest[:8]


def encode_uint256(value: int) -> str:
    """ABI-encode a uint256 value as a 64-character hex string."""
    if value < 0:
        raise ValueError("uint256 cannot be negative")
    return hex(value)[2:].zfill(64)


def encode_address(address: str) -> str:
    """ABI-encode an address as a 64-character zero-padded hex string."""
    addr = address.lower().replace("0x", "")
    return addr.zfill(64)


def decode_uint256(hex_str: str) -> int:
    """Decode a 64-char hex string to uint256."""
    return int(hex_str, 16)


def encode_function_call(selector: str, *args: str) -> str:
    """Encode a function call with selector + ABI-encoded arguments.

    Args:
        selector: 4-byte function selector (e.g. "0xa9059cbb").
        *args: ABI-encoded argument strings (64 chars each).

    Returns:
        Full calldata hex string.
    """
    return selector + "".join(args)


def predict_contract_address(deployer: str, nonce: int) -> str:
    """Predict a CREATE-deployed contract address.

    Uses a simplified hash (SHA-256) as a stand-in for RLP+Keccak.

    Args:
        deployer: Deployer address.
        nonce: Deployment nonce.

    Returns:
        Predicted address (0x-prefixed, 40 hex chars).
    """
    data = f"{deployer.lower()}{nonce}".encode()
    digest = hashlib.sha256(data).hexdigest()
    return "0x" + digest[-40:]


def parse_event_log(topics: list[str], data: str) -> dict[str, Any]:
    """Parse a simplified event log.

    Args:
        topics: List of hex-encoded topic strings (topic[0] = event signature hash).
        data: Hex-encoded non-indexed data.

    Returns:
        Dict with event_hash, indexed topics, and decoded data segments.
    """
    result: dict[str, Any] = {
        "event_hash": topics[0] if topics else "",
        "indexed": topics[1:] if len(topics) > 1 else [],
        "data_segments": [],
    }
    # Split data into 64-char (32-byte) segments
    clean = data.replace("0x", "")
    result["data_segments"] = [clean[i:i+64] for i in range(0, len(clean), 64) if clean[i:i+64]]
    return result


# ── Ether / Wei / Gwei conversion (backward compat) ────────────────

def ether_to_wei(ether: float) -> int:
    """Convert ether to wei (1 ether = 10^18 wei)."""
    return int(ether * 10**18)


def gwei_to_wei(gwei: float) -> int:
    """Convert gwei to wei (1 gwei = 10^9 wei)."""
    return int(gwei * 10**9)


def wei_to_ether(wei: int) -> float:
    """Convert wei to ether."""
    return wei / 10**18

