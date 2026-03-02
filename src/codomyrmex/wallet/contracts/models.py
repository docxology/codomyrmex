"""Smart contract models and data types."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Network(Enum):
    """Blockchain networks."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BASE = "base"
    SOLANA = "solana"


class TransactionStatus(Enum):
    """Transaction status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


@dataclass
class Address:
    """Blockchain address."""
    value: str
    network: Network = Network.ETHEREUM

    def __str__(self) -> str:
        """str ."""
        return self.value

    @property
    def is_valid(self) -> bool:
        if self.network in [Network.ETHEREUM, Network.POLYGON, Network.ARBITRUM, Network.OPTIMISM, Network.BASE]:
            return len(self.value) == 42 and self.value.startswith("0x")
        return len(self.value) > 0


@dataclass
class Transaction:
    """A blockchain transaction."""
    hash: str
    from_address: Address
    to_address: Address
    value: int  # In wei/lamports
    data: str = ""
    gas_limit: int = 21000
    gas_price: int = 0
    nonce: int = 0
    status: TransactionStatus = TransactionStatus.PENDING
    block_number: int | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ContractFunction:
    """A smart contract function."""
    name: str
    inputs: list[dict[str, str]] = field(default_factory=list)
    outputs: list[dict[str, str]] = field(default_factory=list)
    payable: bool = False
    view: bool = False

    def encode_call(self, *args) -> str:
        """Encode function call data (simplified)."""
        selector = hashlib.sha3_256(
            f"{self.name}({','.join(i['type'] for i in self.inputs)})".encode()
        ).hexdigest()[:8]
        return f"0x{selector}"
