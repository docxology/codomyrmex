"""
Smart Contracts Module

Web3 and blockchain smart contract interfaces.
"""

__version__ = "0.1.0"

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import hashlib
import json


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
    block_number: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ContractFunction:
    """A smart contract function."""
    name: str
    inputs: List[Dict[str, str]] = field(default_factory=list)
    outputs: List[Dict[str, str]] = field(default_factory=list)
    payable: bool = False
    view: bool = False
    
    def encode_call(self, *args) -> str:
        """Encode function call data (simplified)."""
        selector = hashlib.sha3_256(
            f"{self.name}({','.join(i['type'] for i in self.inputs)})".encode()
        ).hexdigest()[:8]
        return f"0x{selector}"


@dataclass
class Contract:
    """A smart contract."""
    address: Address
    abi: List[Dict[str, Any]] = field(default_factory=list)
    name: str = ""
    
    def __post_init__(self):
        self._functions: Dict[str, ContractFunction] = {}
        for item in self.abi:
            if item.get("type") == "function":
                func = ContractFunction(
                    name=item["name"],
                    inputs=item.get("inputs", []),
                    outputs=item.get("outputs", []),
                    payable=item.get("payable", False),
                    view=item.get("stateMutability") == "view",
                )
                self._functions[item["name"]] = func
    
    def get_function(self, name: str) -> Optional[ContractFunction]:
        return self._functions.get(name)
    
    def list_functions(self) -> List[str]:
        return list(self._functions.keys())


class ContractCall:
    """Build and execute contract calls."""
    
    def __init__(self, contract: Contract, function_name: str):
        self.contract = contract
        self.function_name = function_name
        self._args: List[Any] = []
        self._value: int = 0
        self._gas_limit: int = 100000
    
    def with_args(self, *args) -> "ContractCall":
        self._args = list(args)
        return self
    
    def with_value(self, value: int) -> "ContractCall":
        self._value = value
        return self
    
    def with_gas_limit(self, limit: int) -> "ContractCall":
        self._gas_limit = limit
        return self
    
    def encode(self) -> str:
        """Encode the call data."""
        func = self.contract.get_function(self.function_name)
        if not func:
            raise ValueError(f"Function not found: {self.function_name}")
        return func.encode_call(*self._args)
    
    def to_transaction(self, from_address: Address, nonce: int = 0) -> Transaction:
        """Build transaction for this call."""
        return Transaction(
            hash="",
            from_address=from_address,
            to_address=self.contract.address,
            value=self._value,
            data=self.encode(),
            gas_limit=self._gas_limit,
            nonce=nonce,
        )


class TransactionBuilder:
    """Build transactions with fluent API."""
    
    def __init__(self, from_address: Address):
        self.from_address = from_address
        self._to: Optional[Address] = None
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


class ContractRegistry:
    """Registry of known contracts."""
    
    def __init__(self):
        self._contracts: Dict[str, Contract] = {}
    
    def register(self, name: str, contract: Contract) -> None:
        self._contracts[name] = contract
    
    def get(self, name: str) -> Optional[Contract]:
        return self._contracts.get(name)
    
    def list(self) -> List[str]:
        return list(self._contracts.keys())


# Utility functions
def wei_to_ether(wei: int) -> float:
    return wei / 10**18


def ether_to_wei(ether: float) -> int:
    return int(ether * 10**18)


def gwei_to_wei(gwei: float) -> int:
    return int(gwei * 10**9)


__all__ = [
    "Network",
    "Address",
    "Transaction",
    "TransactionStatus",
    "Contract",
    "ContractFunction",
    "ContractCall",
    "TransactionBuilder",
    "ContractRegistry",
    "wei_to_ether",
    "ether_to_wei",
    "gwei_to_wei",
]
