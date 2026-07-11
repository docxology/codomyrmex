"""MCP tool definitions for the wallet module.

Exposes wallet creation, listing, and status checks as MCP tools.
Key management operations use the encryption module's KeyManager.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_wallet_manager(storage_path: str | None = None):
    """Lazy import and create a WalletManager."""
    from pathlib import Path

    from codomyrmex.wallet.core import WalletManager

    path = Path(storage_path) if storage_path else None
    return WalletManager(storage_path=path)


@mcp_tool(
    category="wallet",
    description="Create a new self-custody wallet for a user with secure key storage.",
)
def wallet_create(
    user_id: str,
    storage_path: str | None = None,
) -> dict[str, Any]:
    """Create a new wallet for the specified user.

    Args:
        user_id: Unique identifier for the wallet owner.
        storage_path: Optional directory for key storage.

    Returns:
        dict with keys: status, user_id, wallet_address
    """
    try:
        mgr = _get_wallet_manager(storage_path)
        address = mgr.create_wallet(user_id)
        return {
            "status": "success",
            "user_id": user_id,
            "wallet_address": address,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="wallet",
    description="Check if a user has a wallet and return its address.",
)
def wallet_get_address(
    user_id: str,
    storage_path: str | None = None,
) -> dict[str, Any]:
    """Get a user's wallet address if it exists.

    Args:
        user_id: The user identifier.
        storage_path: Optional directory for key storage.

    Returns:
        dict with keys: status, user_id, has_wallet, wallet_address
    """
    try:
        mgr = _get_wallet_manager(storage_path)
        has = mgr.has_wallet(user_id)
        address = mgr.get_wallet_address(user_id)
        return {
            "status": "success",
            "user_id": user_id,
            "has_wallet": has,
            "wallet_address": address,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="wallet",
    description="list all registered wallets mapping user IDs to addresses.",
)
def wallet_list(
    storage_path: str | None = None,
) -> dict[str, Any]:
    """list all registered wallets.

    Args:
        storage_path: Optional directory for key storage.

    Returns:
        dict with keys: status, wallets, count
    """
    try:
        mgr = _get_wallet_manager(storage_path)
        wallets = mgr.list_wallets()
        return {
            "status": "success",
            "wallets": wallets,
            "count": len(wallets),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="wallet",
    description=(
        "Generate a zero-knowledge proof of wallet ownership without "
        "revealing the private key. Uses Fiat-Shamir non-interactive "
        "challenge–response (HMAC-SHA256)."
    ),
)
def wallet_generate_zk_proof(
    user_id: str,
    storage_path: str | None = None,
    message: str = "",
    wallet_address: str | None = None,
) -> dict[str, Any]:
    """Generate a ZK proof that the caller owns the wallet for ``user_id``.

    The proof reveals ``HMAC(private_key, challenge)`` — never the raw key.

    Args:
        user_id: The wallet owner identifier.
        storage_path: Optional directory for key storage.
        message: Optional message string the proof covers (e.g. a tx hash).
        wallet_address: The wallet address. Required when ``storage_path``
            is provided and the wallet was created by a previous call
            (the key is on disk but the in-memory registry is fresh).

    Returns:
        dict with keys: status, proof (or message on error).
    """
    from codomyrmex.wallet.zk_proof import generate_zk_proof

    result = generate_zk_proof(
        user_id,
        storage_path=storage_path,
        message=message,
        wallet_address=wallet_address,
    )
    if "status" in result and result["status"] == "error":
        return result
    return {"status": "success", "proof": result}


@mcp_tool(
    category="wallet",
    description=(
        "Verify a zero-knowledge proof of wallet ownership. Re-derives "
        "the challenge (Fiat-Shamir) and checks the HMAC response."
    ),
)
def wallet_verify_zk_proof(
    proof: dict[str, Any],
    storage_path: str | None = None,
    message: str = "",
) -> dict[str, Any]:
    """Verify a ZK proof of wallet ownership.

    Args:
        proof: The proof dict (from ``wallet_generate_zk_proof``).
        storage_path: Optional directory for key storage.
        message: Optional message string the proof covers.

    Returns:
        dict with keys: status, verified.
    """
    from codomyrmex.wallet.zk_proof import verify_zk_proof

    return verify_zk_proof(proof, storage_path=storage_path, message=message)
