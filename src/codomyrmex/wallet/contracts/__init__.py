"""
Smart Contracts Module

Web3 and blockchain smart contract interfaces.
"""

__version__ = "0.1.0"

from .builders import TransactionBuilder
from .contract import Contract, ContractCall
from .events import ContractEvent, EventFilter, EventLog
from .models import (
    Address,
    ContractFunction,
    Network,
    Transaction,
    TransactionStatus,
)
from .registry import ContractRegistry
from .utils import ether_to_wei, gwei_to_wei, wei_to_ether

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the smart_contracts module."""

    def _registry():
        """List registered contracts."""
        reg = ContractRegistry()
        contracts = reg.list_contracts()
        print("Smart Contract Registry")
        print(f"  Networks: {[n.value for n in Network]}")
        print(f"  Registered Contracts: {len(contracts)}")
        for c in contracts:
            print(f"    - {c.name} @ {c.address}")

    def _validate(address: str = ""):
        """Validate a contract."""
        if not address:
            print("Usage: smart_contracts validate --address <contract_address>")
            return
        try:
            addr = Address(address)
            print(f"Address format valid: {addr}")
            print(f"  Transaction statuses: {[s.value for s in TransactionStatus]}")
        except Exception as e:
            print(f"Validation error: {e}")

    return {
        "registry": _registry,
        "validate": _validate,
    }


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
    "cli_commands",
]
