"""
Smart Contracts Module

Web3 and blockchain smart contract interfaces.
"""

__version__ = "0.1.0"

from .models import (
    Address,
    ContractFunction,
    Network,
    Transaction,
    TransactionStatus,
)
from .contract import Contract, ContractCall
from .builders import TransactionBuilder
from .registry import ContractRegistry
from .events import ContractEvent, EventFilter, EventLog
from .utils import ether_to_wei, gwei_to_wei, wei_to_ether

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
    "ContractEvent",
    "EventFilter",
    "EventLog",
    "wei_to_ether",
    "ether_to_wei",
    "gwei_to_wei",
]
