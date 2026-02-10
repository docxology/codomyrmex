"""Contract registry for managing known contracts."""

from .contract import Contract


class ContractRegistry:
    """Registry of known contracts."""

    def __init__(self):
        self._contracts: dict[str, Contract] = {}

    def register(self, name: str, contract: Contract) -> None:
        self._contracts[name] = contract

    def get(self, name: str) -> Contract | None:
        return self._contracts.get(name)

    def remove(self, name: str) -> bool:
        """Remove a contract by name. Returns True if it existed."""
        if name in self._contracts:
            del self._contracts[name]
            return True
        return False

    def list(self) -> list[str]:
        return list(self._contracts.keys())
