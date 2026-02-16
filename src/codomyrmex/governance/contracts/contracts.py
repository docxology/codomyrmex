"""Contract lifecycle management with terms, signing, and compliance checking.

Models contracts between parties with typed terms (obligations, prohibitions,
permissions), multi-party signing workflow, automatic status transitions, and
compliance verification.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ContractStatus(Enum):
    """Lifecycle states for a contract."""

    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    DISPUTED = "disputed"


class ContractError(Exception):
    """Raised on invalid contract operations."""


@dataclass
class ContractTerm:
    """A single clause or obligation within a contract.

    Attributes:
        description: Human-readable description of the term.
        type: One of ``"obligation"``, ``"prohibition"``, or ``"permission"``.
        party: The party responsible for or subject to this term.
        deadline: Optional deadline by which the term must be fulfilled.
        fulfilled: Whether the term has been satisfied.
    """

    description: str
    type: str  # "obligation", "prohibition", "permission"
    party: str
    deadline: Optional[datetime] = None
    fulfilled: bool = False

    VALID_TYPES = ("obligation", "prohibition", "permission")

    def __post_init__(self) -> None:
        if self.type not in self.VALID_TYPES:
            raise ContractError(
                f"Invalid term type '{self.type}'. "
                f"Must be one of: {', '.join(self.VALID_TYPES)}"
            )

    def is_overdue(self) -> bool:
        """Return True if the term has an unfulfilled deadline in the past."""
        if self.fulfilled or self.deadline is None:
            return False
        return datetime.now() > self.deadline

    def fulfill(self) -> None:
        """Mark the term as fulfilled."""
        self.fulfilled = True


class Contract:
    """A multi-party contract with terms, signing, and compliance checking.

    Usage::

        contract = Contract("NDA", ["Alice", "Bob"])
        contract.add_term(ContractTerm(
            description="Parties must not disclose trade secrets",
            type="prohibition",
            party="Alice",
        ))
        contract.sign("Alice")
        contract.sign("Bob")
        print(contract.get_status())  # "active"
        print(contract.check_compliance())
    """

    def __init__(self, title: str, parties: list[str]) -> None:
        """Create a new contract in DRAFT status.

        Args:
            title: Title or subject of the contract.
            parties: List of party names who must sign.

        Raises:
            ContractError: If fewer than 2 parties are specified.
        """
        if len(parties) < 2:
            raise ContractError("A contract requires at least 2 parties.")
        if len(set(parties)) != len(parties):
            raise ContractError("Duplicate party names are not allowed.")

        self.id: str = str(uuid.uuid4())
        self.title: str = title
        self.parties: list[str] = list(parties)
        self.terms: list[ContractTerm] = []
        self.signatures: dict[str, dict] = {}
        self.status: ContractStatus = ContractStatus.DRAFT
        self.created_at: datetime = datetime.now()
        self.expired_at: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Term management
    # ------------------------------------------------------------------

    def add_term(self, term: ContractTerm) -> None:
        """Add a term to the contract.

        Terms can only be added while the contract is in DRAFT status.

        Args:
            term: The term to add.

        Raises:
            ContractError: If the contract is not in DRAFT status, or if the
                term's party is not a party to this contract.
        """
        if self.status != ContractStatus.DRAFT:
            raise ContractError(
                "Terms can only be added to contracts in DRAFT status."
            )
        if term.party not in self.parties:
            raise ContractError(
                f"Party '{term.party}' is not a party to this contract."
            )
        self.terms.append(term)

    # ------------------------------------------------------------------
    # Signing
    # ------------------------------------------------------------------

    def sign(self, party: str, signature: Optional[str] = None) -> bool:
        """Record a party's signature.

        If all parties have signed, the contract transitions to ACTIVE status.

        Args:
            party: The name of the signing party.
            signature: An optional digital signature string.  If ``None``, a
                hash-based signature is generated automatically.

        Returns:
            ``True`` if the signature was recorded.

        Raises:
            ContractError: If the party is not valid, has already signed, or
                the contract is not in DRAFT status.
        """
        if self.status != ContractStatus.DRAFT:
            raise ContractError(
                f"Cannot sign a contract in {self.status.value} status."
            )
        if party not in self.parties:
            raise ContractError(f"'{party}' is not a party to this contract.")
        if party in self.signatures:
            raise ContractError(f"'{party}' has already signed.")

        if signature is None:
            # Generate a deterministic placeholder signature
            sig_input = f"{self.id}:{party}:{datetime.now().isoformat()}"
            signature = hashlib.sha256(sig_input.encode()).hexdigest()[:16]

        self.signatures[party] = {
            "signature": signature,
            "signed_at": datetime.now(),
        }

        # Auto-activate when all parties have signed
        if set(self.signatures.keys()) == set(self.parties):
            self.status = ContractStatus.ACTIVE

        return True

    # ------------------------------------------------------------------
    # Compliance
    # ------------------------------------------------------------------

    def check_compliance(self) -> dict:
        """Evaluate compliance across all terms.

        Returns a dict with:
            - ``total_terms``: Total number of terms.
            - ``fulfilled``: Number of fulfilled terms.
            - ``overdue``: Number of unfulfilled terms past their deadline.
            - ``pending``: Number of unfulfilled terms not yet overdue.
            - ``compliance_rate``: Fraction of terms fulfilled (0.0 - 1.0).
            - ``issues``: List of dicts describing overdue or violated terms.
        """
        fulfilled = 0
        overdue = 0
        pending = 0
        issues: list[dict] = []

        for term in self.terms:
            if term.fulfilled:
                fulfilled += 1
            elif term.is_overdue():
                overdue += 1
                issues.append({
                    "party": term.party,
                    "description": term.description,
                    "type": term.type,
                    "deadline": term.deadline.isoformat() if term.deadline else None,
                    "severity": "overdue",
                })
            else:
                pending += 1

        total = len(self.terms)
        compliance_rate = fulfilled / total if total > 0 else 1.0

        return {
            "total_terms": total,
            "fulfilled": fulfilled,
            "overdue": overdue,
            "pending": pending,
            "compliance_rate": round(compliance_rate, 4),
            "issues": issues,
        }

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def is_active(self) -> bool:
        """Return True if the contract is currently active."""
        return self.status == ContractStatus.ACTIVE

    def expire(self) -> None:
        """Transition the contract to EXPIRED status.

        Raises:
            ContractError: If the contract is not ACTIVE.
        """
        if self.status != ContractStatus.ACTIVE:
            raise ContractError("Only active contracts can expire.")
        self.status = ContractStatus.EXPIRED
        self.expired_at = datetime.now()

    def get_status(self) -> str:
        """Return the current status as a string."""
        return self.status.value

    def __repr__(self) -> str:
        return (
            f"Contract(id={self.id[:8]}..., title={self.title!r}, "
            f"status={self.status.value}, "
            f"signed={len(self.signatures)}/{len(self.parties)})"
        )
