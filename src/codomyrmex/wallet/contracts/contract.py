"""Smart contract and contract call interfaces."""

from typing import Any

from .models import Address, ContractFunction, Transaction


class Contract:
    """A smart contract."""

    def __init__(self, address: Address, abi: list[dict[str, Any]] = None, name: str = ""):
        self.address = address
        self.abi = abi or []
        self.name = name
        self._functions: dict[str, ContractFunction] = {}
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

    def get_function(self, name: str) -> ContractFunction | None:
        return self._functions.get(name)

    def list_functions(self) -> list[str]:
        return list(self._functions.keys())

    @property
    def function_count(self) -> int:
        return len(self._functions)

    def view_functions(self) -> list[str]:
        """Return names of view (read-only) functions."""
        return [n for n, f in self._functions.items() if f.view]

    def payable_functions(self) -> list[str]:
        """Return names of payable functions."""
        return [n for n, f in self._functions.items() if f.payable]

    def validate(self) -> list[str]:
        """Validate the contract configuration."""
        issues: list[str] = []
        if not self.address:
            issues.append("Contract address is required")
        if not self.abi:
            issues.append("ABI is empty")
        return issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "address": self.address,
            "name": self.name,
            "functions": self.list_functions(),
            "function_count": self.function_count,
        }



class ContractCall:
    """Build and execute contract calls."""

    def __init__(self, contract: Contract, function_name: str):
        self.contract = contract
        self.function_name = function_name
        self._args: list[Any] = []
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
