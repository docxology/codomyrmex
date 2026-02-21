"""Transaction builder with fluent API, batch mode, and estimation.

Provides:
- TransactionBuilder: fluent API for constructing transactions
- Batch transaction creation
- Gas estimation helpers
- Transaction validation
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from .models import Address, Transaction


# ── Gas estimation constants ────────────────────────────────────────

BASE_GAS = 21_000
DATA_GAS_PER_BYTE = 68
DATA_GAS_PER_ZERO_BYTE = 4
CONTRACT_CREATION_GAS = 53_000


def estimate_gas(data: str = "", is_contract_creation: bool = False) -> int:
    """Estimate gas for a transaction based on calldata.

    Args:
        data: Hex-encoded calldata (without 0x prefix).
        is_contract_creation: True if deploying a contract.

    Returns:
        Estimated gas units.
    """
    base = CONTRACT_CREATION_GAS if is_contract_creation else BASE_GAS
    if not data:
        return base
    clean = data.replace("0x", "")
    byte_data = bytes.fromhex(clean) if len(clean) % 2 == 0 else b""
    gas = base
    for b in byte_data:
        gas += DATA_GAS_PER_ZERO_BYTE if b == 0 else DATA_GAS_PER_BYTE
    return gas


class TransactionBuilder:
    """Build transactions with a fluent API.

    Example::

        tx = (TransactionBuilder("0xSender")
              .to("0xReceiver")
              .value(1000)
              .gas_limit(21000)
              .build())
    """

    def __init__(self, from_address: Address) -> None:
        self.from_address = from_address
        self._to: Address | None = None
        self._value: int = 0
        self._data: str = ""
        self._gas_limit: int = 21000
        self._gas_price: int = 0
        self._nonce: int = 0
        self._chain_id: int = 1
        self._memo: str = ""

    def to(self, address: Address) -> "TransactionBuilder":
        self._to = address
        return self

    def value(self, amount: int) -> "TransactionBuilder":
        self._value = amount
        return self

    def data(self, data: str) -> "TransactionBuilder":
        self._data = data
        return self

    def gas_limit(self, limit: int) -> "TransactionBuilder":
        self._gas_limit = limit
        return self

    def gas_price(self, price: int) -> "TransactionBuilder":
        self._gas_price = price
        return self

    def nonce(self, nonce: int) -> "TransactionBuilder":
        self._nonce = nonce
        return self

    def chain_id(self, cid: int) -> "TransactionBuilder":
        self._chain_id = cid
        return self

    def memo(self, memo: str) -> "TransactionBuilder":
        self._memo = memo
        return self

    def auto_gas(self) -> "TransactionBuilder":
        """Auto-estimate gas from calldata."""
        self._gas_limit = estimate_gas(self._data, is_contract_creation=(self._to is None))
        return self

    def validate(self) -> list[str]:
        """Validate the transaction before building."""
        issues: list[str] = []
        if not self.from_address:
            issues.append("from_address is required")
        if self._to is None and not self._data:
            issues.append("Contract creation requires data")
        if self._value < 0:
            issues.append("value cannot be negative")
        if self._gas_limit < BASE_GAS:
            issues.append(f"gas_limit must be >= {BASE_GAS}")
        if self._nonce < 0:
            issues.append("nonce cannot be negative")
        return issues

    def build(self) -> Transaction:
        """Build and return the Transaction."""
        if not self._to:
            raise ValueError("To address is required")

        tx_hash = hashlib.sha256(
            f"{self.from_address}{self._to}{self._value}{self._nonce}{self._chain_id}".encode()
        ).hexdigest()

        return Transaction(
            hash=f"0x{tx_hash[:64]}",
            from_address=self.from_address,
            to_address=self._to,
            value=self._value,
            data=self._data,
            gas_limit=self._gas_limit,
            gas_price=self._gas_price,
            nonce=self._nonce,
        )


# ── Batch builder ───────────────────────────────────────────────────

def build_batch(
    from_address: Address,
    transfers: list[dict[str, Any]],
    starting_nonce: int = 0,
    gas_price: int = 0,
) -> list[Transaction]:
    """Build multiple transactions from a list of transfer specs.

    Args:
        from_address: Sender address.
        transfers: List of {"to": address, "value": amount} dicts.
        starting_nonce: First nonce to use (auto-incremented).
        gas_price: Gas price for all transactions.

    Returns:
        List of built Transaction objects.
    """
    txs: list[Transaction] = []
    for i, spec in enumerate(transfers):
        builder = (
            TransactionBuilder(from_address)
            .to(spec["to"])
            .value(spec.get("value", 0))
            .nonce(starting_nonce + i)
            .gas_price(gas_price)
        )
        if "data" in spec:
            builder.data(spec["data"])
        txs.append(builder.build())
    return txs
