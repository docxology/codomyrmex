"""Contract registry with versioning, search, and lifecycle management.

Provides:
- ContractRegistry: named contract storage with versioning
- Version history tracking
- Tag-based and status-based filtering
- Contract lifecycle (deploy → active → deprecated → archived)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from .contract import Contract


class ContractStatus(Enum):
    """Functional component: ContractStatus."""
    DRAFT = auto()
    DEPLOYED = auto()
    ACTIVE = auto()
    DEPRECATED = auto()
    ARCHIVED = auto()


@dataclass
class ContractVersion:
    """A versioned snapshot of a contract."""

    version: int
    contract: Contract
    status: ContractStatus = ContractStatus.DRAFT
    deployed_at: float | None = None
    tags: set[str] = field(default_factory=set)
    notes: str = ""


class ContractRegistry:
    """Registry of known contracts with versioning and lifecycle.

    Example::

        reg = ContractRegistry()
        reg.register("token", contract, tags={"erc20", "mainnet"})
        reg.deploy("token")
        reg.deprecate("token")
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._contracts: dict[str, ContractVersion] = {}
        self._history: dict[str, list[ContractVersion]] = {}

    def register(self, name: str, contract: Contract, tags: set[str] | None = None, notes: str = "") -> None:
        """Register a contract with optional tags."""
        version_num = len(self._history.get(name, [])) + 1
        entry = ContractVersion(
            version=version_num,
            contract=contract,
            tags=tags or set(),
            notes=notes,
        )
        self._contracts[name] = entry
        self._history.setdefault(name, []).append(entry)

    def get(self, name: str) -> Contract | None:
        """Get the current contract by name."""
        entry = self._contracts.get(name)
        return entry.contract if entry else None

    def get_version(self, name: str) -> ContractVersion | None:
        """Get the full version entry."""
        return self._contracts.get(name)

    def remove(self, name: str) -> bool:
        """Remove a contract by name."""
        if name in self._contracts:
            del self._contracts[name]
            return True
        return False

    def list(self) -> list[str]:
        """List all registered contract names."""
        return sorted(self._contracts.keys())

    # ── Lifecycle management ────────────────────────────────────────

    def deploy(self, name: str) -> bool:
        """Mark a contract as deployed."""
        entry = self._contracts.get(name)
        if entry and entry.status in (ContractStatus.DRAFT,):
            entry.status = ContractStatus.DEPLOYED
            entry.deployed_at = time.time()
            return True
        return False

    def activate(self, name: str) -> bool:
        """Mark a deployed contract as active."""
        entry = self._contracts.get(name)
        if entry and entry.status == ContractStatus.DEPLOYED:
            entry.status = ContractStatus.ACTIVE
            return True
        return False

    def deprecate(self, name: str) -> bool:
        """Mark a contract as deprecated."""
        entry = self._contracts.get(name)
        if entry and entry.status in (ContractStatus.DEPLOYED, ContractStatus.ACTIVE):
            entry.status = ContractStatus.DEPRECATED
            return True
        return False

    def archive(self, name: str) -> bool:
        """Archive a deprecated contract."""
        entry = self._contracts.get(name)
        if entry and entry.status == ContractStatus.DEPRECATED:
            entry.status = ContractStatus.ARCHIVED
            return True
        return False

    # ── Search and filter ───────────────────────────────────────────

    def filter_by_status(self, status: ContractStatus) -> list[str]:
        """Return contract names with a specific status."""
        return [name for name, entry in self._contracts.items() if entry.status == status]

    def filter_by_tag(self, tag: str) -> list[str]:
        """Return contract names that have a specific tag."""
        return [name for name, entry in self._contracts.items() if tag in entry.tags]

    def get_history(self, name: str) -> list[ContractVersion]:
        """Get all version history for a contract."""
        return list(self._history.get(name, []))

    @property
    def count(self) -> int:
        """count ."""
        return len(self._contracts)

    def summary(self) -> dict[str, Any]:
        """Registry summary."""
        return {
            "total": self.count,
            "by_status": {
                status.name: len(self.filter_by_status(status))
                for status in ContractStatus
            },
        }
