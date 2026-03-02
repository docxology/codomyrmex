"""Governance contracts module.

Provides ContractStatus, ContractTerm, Contract, and ContractError
for modeling inter-agent governance contracts.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class ContractStatus(Enum):
    """Status of a governance contract."""
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    DISPUTED = "disputed"


class ContractError(Exception):
    """Base exception for contract errors."""
    pass


_VALID_TERM_TYPES = {"obligation", "prohibition", "permission"}


@dataclass
class ContractTerm:
    """A term or clause in a contract.

    Args:
        description: Human-readable description of the term.
        type: One of 'obligation', 'prohibition', 'permission'.
        party: The party this term applies to.
        deadline: Optional deadline for the term.
        fulfilled: Whether the term has been fulfilled.
    """
    description: str
    type: str
    party: str
    deadline: datetime | None = None
    fulfilled: bool = False

    def __post_init__(self) -> None:
        """post Init ."""
        if self.type not in _VALID_TERM_TYPES:
            raise ContractError(
                f"Invalid term type '{self.type}'. "
                f"Must be one of: {', '.join(sorted(_VALID_TERM_TYPES))}"
            )

    def fulfill(self) -> None:
        """Mark this term as fulfilled."""
        self.fulfilled = True

    def is_overdue(self) -> bool:
        """Check whether this term is past its deadline and unfulfilled."""
        if self.fulfilled:
            return False
        if self.deadline is None:
            return False
        return datetime.now() > self.deadline


class Contract:
    """Represents a governance contract between agents.

    Args:
        title: Contract title.
        parties: List of party names (at least 2, no duplicates).
    """

    def __init__(self, title: str, parties: list[str]) -> None:
        """Initialize this instance."""
        if len(parties) < 2:
            raise ContractError("Contract requires at least 2 parties")
        if len(parties) != len(set(parties)):
            raise ContractError("Duplicate parties are not allowed")

        self.id = uuid4()
        self.title = title
        self.parties = parties
        self.status = ContractStatus.DRAFT
        self.terms: list[ContractTerm] = []
        self.signatures: dict[str, dict[str, Any]] = {}
        self.created_at = datetime.now()
        self.expired_at: datetime | None = None

    # ------------------------------------------------------------------
    # Terms
    # ------------------------------------------------------------------

    def add_term(self, term: ContractTerm) -> None:
        """Add a term to a DRAFT contract.

        Raises:
            ContractError: If contract is not DRAFT or party is invalid.
        """
        if self.status != ContractStatus.DRAFT:
            raise ContractError("Terms can only be added to a DRAFT contract")
        if term.party not in self.parties:
            raise ContractError(f"'{term.party}' is not a party to this contract")
        self.terms.append(term)

    # ------------------------------------------------------------------
    # Signing
    # ------------------------------------------------------------------

    def sign(self, party: str, *, signature: str = "") -> bool:
        """Sign the contract on behalf of a party.

        Auto-activates when all parties have signed.

        Args:
            party: Name of the signing party.
            signature: Optional custom signature string.

        Returns:
            True on success.

        Raises:
            ContractError: If party is invalid, already signed, or contract
                           is not in DRAFT status.
        """
        if self.status != ContractStatus.DRAFT:
            raise ContractError("Only DRAFT contracts can be signed")
        if party not in self.parties:
            raise ContractError(f"'{party}' is not a party to this contract")
        if party in self.signatures:
            raise ContractError(f"'{party}' has already signed this contract")

        self.signatures[party] = {
            "signed_at": datetime.now(),
            "signature": signature or f"sig-{party}-{uuid4().hex[:8]}",
        }

        # Auto-activate when all parties have signed
        if set(self.signatures.keys()) == set(self.parties):
            self.status = ContractStatus.ACTIVE

        return True

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def expire(self) -> None:
        """Transition an ACTIVE contract to EXPIRED.

        Raises:
            ContractError: If contract is not ACTIVE.
        """
        if self.status != ContractStatus.ACTIVE:
            raise ContractError("Only active contracts can be expired")
        self.status = ContractStatus.EXPIRED
        self.expired_at = datetime.now()

    def terminate(self, reason: str = "") -> None:
        """Terminate the contract.

        Raises:
            ContractError: If contract is already terminated.
        """
        if self.status == ContractStatus.TERMINATED:
            raise ContractError("Contract is already terminated")
        self.status = ContractStatus.TERMINATED

    def dispute(self, reason: str = "") -> None:
        """Mark the contract as disputed.

        Raises:
            ContractError: If contract is not ACTIVE.
        """
        if self.status != ContractStatus.ACTIVE:
            raise ContractError("Only active contracts can be disputed")
        self.status = ContractStatus.DISPUTED

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def is_active(self) -> bool:
        """Return True if contract is in ACTIVE status."""
        return self.status == ContractStatus.ACTIVE

    def get_status(self) -> str:
        """Return the current status as a string."""
        return self.status.value

    def check_compliance(self) -> dict[str, Any]:
        """Check compliance across all terms.

        Returns:
            Dict with total_terms, fulfilled, overdue, pending,
            compliance_rate, and issues list.
        """
        total = len(self.terms)
        if total == 0:
            return {
                "total_terms": 0,
                "fulfilled": 0,
                "overdue": 0,
                "pending": 0,
                "compliance_rate": 1.0,
                "issues": [],
            }

        fulfilled = sum(1 for t in self.terms if t.fulfilled)
        overdue = sum(1 for t in self.terms if t.is_overdue())
        pending = total - fulfilled - overdue

        issues = []
        for t in self.terms:
            if t.is_overdue():
                issues.append({
                    "description": t.description,
                    "party": t.party,
                    "severity": "overdue",
                })

        compliance_rate = fulfilled / total if total > 0 else 1.0

        return {
            "total_terms": total,
            "fulfilled": fulfilled,
            "overdue": overdue,
            "pending": pending,
            "compliance_rate": compliance_rate,
            "issues": issues,
        }

    def __repr__(self) -> str:
        """repr ."""
        return (
            f"Contract(title='{self.title}', status='{self.status.value}', "
            f"parties={self.parties})"
        )
