from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto


class DisputeStatus(Enum):
    """Functional component: DisputeStatus."""
    OPEN = auto()
    UNDER_REVIEW = auto()
    RESOLVED = auto()
    CLOSED = auto()

class DisputeError(Exception):
    """Exception raised for dispute-related errors."""
    pass

@dataclass
class Dispute:
    """Functional component: Dispute."""
    id: str
    contract_id: str
    filer_id: str
    description: str
    status: DisputeStatus = DisputeStatus.OPEN
    created_at: datetime = field(default_factory=datetime.now)
    resolution: str | None = None

class DisputeResolver:
    """Handles and resolves disputes between parties."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self._disputes: dict[str, Dispute] = {}

    def file_dispute(self, dispute: Dispute) -> None:
        """Execute File Dispute operations natively."""
        if dispute.id in self._disputes:
            raise DisputeError(f"Dispute {dispute.id} already exists.")
        self._disputes[dispute.id] = dispute

    def resolve_dispute(self, dispute_id: str, resolution: str) -> None:
        """Execute Resolve Dispute operations natively."""
        if dispute_id not in self._disputes:
            raise DisputeError(f"Dispute {dispute_id} not found.")

        dispute = self._disputes[dispute_id]
        dispute.resolution = resolution
        dispute.status = DisputeStatus.RESOLVED

    def get_dispute(self, dispute_id: str) -> Dispute | None:
        """Execute Get Dispute operations natively."""
        return self._disputes.get(dispute_id)
