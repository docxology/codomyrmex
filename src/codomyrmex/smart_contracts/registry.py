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

    def list(self) -> list[str]:
        return list(self._contracts.keys())
