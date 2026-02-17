"""Transaction builder with fluent API."""

import hashlib

from .models import Address, Transaction


class TransactionBuilder:
    """Build transactions with fluent API."""

    def __init__(self, from_address: Address):
        self.from_address = from_address
        self._to: Address | None = None
        self._value: int = 0
        self._data: str = ""
        self._gas_limit: int = 21000
        self._gas_price: int = 0
        self._nonce: int = 0

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

    def build(self) -> Transaction:
        if not self._to:
            raise ValueError("To address is required")

        tx_hash = hashlib.sha256(
            f"{self.from_address}{self._to}{self._value}{self._nonce}".encode()
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
