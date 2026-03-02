"""Wallet module exceptions with structured error codes.

Provides:
- WalletError: base exception for all wallet operations
- WalletNotFoundError: wallet does not exist
- WalletKeyError: key storage or retrieval failure
- RitualError: recovery ritual failure
- InsufficientFundsError: not enough balance for operation
- TransactionError: transaction construction or submission failure
- ContractError: smart contract interaction failure
"""

from __future__ import annotations

from typing import Any

from codomyrmex.exceptions import CodomyrmexError


class WalletError(CodomyrmexError):
    """Base exception for wallet operations."""

    def __init__(self, message: str = "", code: str = "", details: dict[str, Any] | None = None) -> None:
        """Initialize this instance."""
        self.code = code
        self.details = details or {}
        super().__init__(message)

    @property
    def error_dict(self) -> dict[str, Any]:
        """error Dict ."""
        return {
            "error_type": self.__class__.__name__,
            "code": self.code,
            "message": str(self),
            "details": self.details,
        }


class WalletNotFoundError(WalletError):
    """Raised when a wallet does not exist for the given user."""

    def __init__(self, user_id: str = "", message: str = "Wallet not found") -> None:
        """Initialize this instance."""
        self.user_id = user_id
        final_msg = f"{message}: {user_id}" if user_id else message
        super().__init__(final_msg, code="WALLET_NOT_FOUND", details={"user_id": user_id})


class WalletKeyError(WalletError):
    """Raised when key storage or retrieval fails."""

    def __init__(self, message: str = "Key operation failed", key_type: str = "") -> None:
        """Initialize this instance."""
        self.key_type = key_type
        super().__init__(message, code="KEY_ERROR", details={"key_type": key_type})


class RitualError(WalletError):
    """Raised when a recovery ritual operation fails."""

    def __init__(self, message: str = "Ritual failed", ritual_step: str = "") -> None:
        """Initialize this instance."""
        self.ritual_step = ritual_step
        super().__init__(message, code="RITUAL_ERROR", details={"ritual_step": ritual_step})


class InsufficientFundsError(WalletError):
    """Raised when the wallet has insufficient balance."""

    def __init__(
        self,
        required: float = 0,
        available: float = 0,
        currency: str = "ETH",
    ) -> None:
        """Initialize this instance."""
        self.required = required
        self.available = available
        self.currency = currency
        super().__init__(
            f"Insufficient {currency}: need {required}, have {available}",
            code="INSUFFICIENT_FUNDS",
            details={"required": required, "available": available, "currency": currency},
        )


class TransactionError(WalletError):
    """Raised when transaction construction or submission fails."""

    def __init__(
        self,
        message: str = "Transaction failed",
        tx_hash: str = "",
        reason: str = "",
    ) -> None:
        """Initialize this instance."""
        self.tx_hash = tx_hash
        self.reason = reason
        super().__init__(message, code="TX_ERROR", details={"tx_hash": tx_hash, "reason": reason})


class ContractError(WalletError):
    """Raised when smart contract interaction fails."""

    def __init__(
        self,
        message: str = "Contract error",
        contract_address: str = "",
        function_name: str = "",
    ) -> None:
        """Initialize this instance."""
        self.contract_address = contract_address
        self.function_name = function_name
        super().__init__(message, code="CONTRACT_ERROR", details={
            "contract_address": contract_address,
            "function_name": function_name,
        })


class GasEstimationError(WalletError):
    """Raised when gas estimation fails."""

    def __init__(self, message: str = "Gas estimation failed") -> None:
        """Initialize this instance."""
        super().__init__(message, code="GAS_ESTIMATION_ERROR")
