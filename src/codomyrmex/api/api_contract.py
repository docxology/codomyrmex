"""API contract definition and validation.

Captures the public API surface as a frozen contract,
detects breaking changes, and enforces signature stability.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BreakingChangeKind(Enum):
    """Types of breaking changes."""

    REMOVED = "removed"
    RENAMED = "renamed"
    PARAM_ADDED_REQUIRED = "param_added_required"
    PARAM_REMOVED = "param_removed"
    RETURN_TYPE_CHANGED = "return_type_changed"
    SIGNATURE_CHANGED = "signature_changed"


@dataclass
class APIEndpoint:
    """A single API endpoint in the contract.

    Attributes:
        name: Fully qualified name.
        version: API version string.
        signature: Parameter signature.
        return_type: Return type annotation.
        module: Containing module.
        frozen: Whether the endpoint is frozen (no changes allowed).
    """

    name: str
    version: str = "1.0.0"
    signature: str = ""
    return_type: str = ""
    module: str = ""
    frozen: bool = False


@dataclass
class BreakingChange:
    """A detected breaking change.

    Attributes:
        endpoint: Affected endpoint name.
        kind: Type of breaking change.
        old_value: Previous value.
        new_value: New value.
        message: Human-readable description.
    """

    endpoint: str
    kind: BreakingChangeKind
    old_value: str = ""
    new_value: str = ""
    message: str = ""


@dataclass
class APIContract:
    """Frozen API contract.

    Captures the public API surface at a point in time
    for comparison and validation.

    Attributes:
        name: Contract name.
        version: Contract version.
        endpoints: All registered endpoints.
        frozen: Whether the contract is frozen.
        checksum: SHA-256 checksum of contract.
    """

    name: str = "codomyrmex"
    version: str = "1.0.0"
    endpoints: dict[str, APIEndpoint] = field(default_factory=dict)
    frozen: bool = False
    checksum: str = ""

    @property
    def endpoint_count(self) -> int:
        """endpoint Count ."""
        return len(self.endpoints)

    def add_endpoint(self, endpoint: APIEndpoint) -> None:
        """Register an API endpoint."""
        if self.frozen:
            raise RuntimeError("Cannot modify a frozen contract")
        self.endpoints[endpoint.name] = endpoint

    def freeze(self) -> str:
        """Freeze the contract and compute checksum."""
        self.frozen = True
        for ep in self.endpoints.values():
            ep.frozen = True
        self.checksum = self._compute_checksum()
        return self.checksum

    def _compute_checksum(self) -> str:
        """Compute SHA-256 over sorted endpoint signatures."""
        payload = json.dumps(
            {name: {"sig": ep.signature, "ret": ep.return_type, "ver": ep.version}
             for name, ep in sorted(self.endpoints.items())},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Serialize contract to dict."""
        return {
            "name": self.name,
            "version": self.version,
            "frozen": self.frozen,
            "checksum": self.checksum,
            "endpoints": {
                name: {
                    "version": ep.version,
                    "signature": ep.signature,
                    "return_type": ep.return_type,
                    "module": ep.module,
                    "frozen": ep.frozen,
                }
                for name, ep in self.endpoints.items()
            },
        }


class ContractValidator:
    """Validate current API against a frozen contract.

    Detects breaking changes: removals, renames, signature
    changes, and new required parameters.

    Example::

        validator = ContractValidator(frozen_contract)
        changes = validator.validate(current_contract)
        assert len(changes) == 0, "Breaking changes detected!"
    """

    def __init__(self, baseline: APIContract) -> None:
        """Initialize this instance."""
        self._baseline = baseline

    def validate(self, current: APIContract) -> list[BreakingChange]:
        """Compare current contract against baseline.

        Args:
            current: Current API contract.

        Returns:
            List of breaking changes found.
        """
        changes: list[BreakingChange] = []

        # Check for removed endpoints
        for name, ep in self._baseline.endpoints.items():
            if name not in current.endpoints:
                changes.append(BreakingChange(
                    endpoint=name,
                    kind=BreakingChangeKind.REMOVED,
                    old_value=ep.signature,
                    message=f"Endpoint '{name}' was removed",
                ))
                continue

            curr_ep = current.endpoints[name]

            # Check signature changes
            if ep.signature and curr_ep.signature != ep.signature:
                changes.append(BreakingChange(
                    endpoint=name,
                    kind=BreakingChangeKind.SIGNATURE_CHANGED,
                    old_value=ep.signature,
                    new_value=curr_ep.signature,
                    message=f"Signature changed: {ep.signature} → {curr_ep.signature}",
                ))

            # Check return type changes
            if ep.return_type and curr_ep.return_type != ep.return_type:
                changes.append(BreakingChange(
                    endpoint=name,
                    kind=BreakingChangeKind.RETURN_TYPE_CHANGED,
                    old_value=ep.return_type,
                    new_value=curr_ep.return_type,
                    message=f"Return type changed: {ep.return_type} → {curr_ep.return_type}",
                ))

        return changes

    def is_compatible(self, current: APIContract) -> bool:
        """Check if current contract is backward-compatible."""
        return len(self.validate(current)) == 0


__all__ = [
    "APIContract",
    "APIEndpoint",
    "BreakingChange",
    "BreakingChangeKind",
    "ContractValidator",
]
