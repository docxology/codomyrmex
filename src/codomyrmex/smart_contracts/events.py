"""Smart contract event models and filtering."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .models import Address


@dataclass
class ContractEvent:
    """A smart contract event."""

    name: str
    args: dict[str, Any] = field(default_factory=dict)
    contract_address: Address | None = None
    block_number: int = 0
    transaction_hash: str = ""
    log_index: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class EventFilter:
    """Filter contract events."""

    def __init__(self):
        self._event_name: str | None = None
        self._from_block: int = 0
        self._to_block: int | None = None
        self._contract_address: Address | None = None

    def event(self, name: str) -> "EventFilter":
        """Filter by event name."""
        self._event_name = name
        return self

    def from_block(self, block: int) -> "EventFilter":
        self._from_block = block
        return self

    def to_block(self, block: int) -> "EventFilter":
        self._to_block = block
        return self

    def address(self, addr: Address) -> "EventFilter":
        self._contract_address = addr
        return self

    def matches(self, event: ContractEvent) -> bool:
        """Check if event matches filter criteria."""
        if self._event_name and event.name != self._event_name:
            return False
        if event.block_number < self._from_block:
            return False
        if self._to_block is not None and event.block_number > self._to_block:
            return False
        if self._contract_address and event.contract_address != self._contract_address:
            return False
        return True


class EventLog:
    """Collect and query contract events."""

    def __init__(self):
        self._events: list[ContractEvent] = []

    def add(self, event: ContractEvent) -> None:
        self._events.append(event)

    def query(self, filter: EventFilter = None) -> list[ContractEvent]:
        """Query events with optional filter."""
        if filter is None:
            return list(self._events)
        return [e for e in self._events if filter.matches(e)]

    def count(self, event_name: str = None) -> int:
        """Count events, optionally by name."""
        if event_name is None:
            return len(self._events)
        return sum(1 for e in self._events if e.name == event_name)

    def latest(self, n: int = 1) -> list[ContractEvent]:
        """Get n most recent events by block number."""
        sorted_events = sorted(
            self._events, key=lambda e: e.block_number, reverse=True
        )
        return sorted_events[:n]
