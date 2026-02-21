"""Smart contract event models, filtering, aggregation, and export.

Provides:
- ContractEvent: event dataclass with block/tx context
- EventFilter: fluent query builder for event matching
- EventLog: event store with query, aggregation, and export
"""

from __future__ import annotations

from collections import defaultdict
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "args": self.args,
            "contract_address": self.contract_address,
            "block_number": self.block_number,
            "transaction_hash": self.transaction_hash,
            "log_index": self.log_index,
            "timestamp": self.timestamp.isoformat(),
        }


class EventFilter:
    """Filter contract events with a fluent API."""

    def __init__(self) -> None:
        self._event_name: str | None = None
        self._from_block: int = 0
        self._to_block: int | None = None
        self._contract_address: Address | None = None
        self._arg_filters: dict[str, Any] = {}

    def event(self, name: str) -> "EventFilter":
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

    def arg_equals(self, key: str, value: Any) -> "EventFilter":
        """Filter by a specific argument value."""
        self._arg_filters[key] = value
        return self

    def matches(self, event: ContractEvent) -> bool:
        """Check if event matches all filter criteria."""
        if self._event_name and event.name != self._event_name:
            return False
        if event.block_number < self._from_block:
            return False
        if self._to_block is not None and event.block_number > self._to_block:
            return False
        if self._contract_address and event.contract_address != self._contract_address:
            return False
        for key, val in self._arg_filters.items():
            if event.args.get(key) != val:
                return False
        return True


class EventLog:
    """Collect, query, and aggregate contract events."""

    def __init__(self) -> None:
        self._events: list[ContractEvent] = []

    def add(self, event: ContractEvent) -> None:
        self._events.append(event)

    def add_many(self, events: list[ContractEvent]) -> None:
        self._events.extend(events)

    def query(self, filter: EventFilter | None = None) -> list[ContractEvent]:
        if filter is None:
            return list(self._events)
        return [e for e in self._events if filter.matches(e)]

    def count(self, event_name: str | None = None) -> int:
        if event_name is None:
            return len(self._events)
        return sum(1 for e in self._events if e.name == event_name)

    def latest(self, n: int = 1) -> list[ContractEvent]:
        sorted_events = sorted(self._events, key=lambda e: e.block_number, reverse=True)
        return sorted_events[:n]

    def event_names(self) -> list[str]:
        """Return unique event names sorted."""
        return sorted({e.name for e in self._events})

    def group_by_name(self) -> dict[str, list[ContractEvent]]:
        """Group events by name."""
        groups: dict[str, list[ContractEvent]] = defaultdict(list)
        for e in self._events:
            groups[e.name].append(e)
        return dict(groups)

    def group_by_block(self) -> dict[int, list[ContractEvent]]:
        """Group events by block number."""
        groups: dict[int, list[ContractEvent]] = defaultdict(list)
        for e in self._events:
            groups[e.block_number].append(e)
        return dict(groups)

    def event_frequency(self) -> dict[str, int]:
        """Count occurrences of each event name."""
        counts: dict[str, int] = defaultdict(int)
        for e in self._events:
            counts[e.name] += 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def export_json(self) -> list[dict[str, Any]]:
        """Export all events as a list of dicts."""
        return [e.to_dict() for e in self._events]

    def clear(self) -> None:
        self._events.clear()

    @property
    def total(self) -> int:
        return len(self._events)

    def summary(self) -> dict[str, Any]:
        """Aggregate summary of event log."""
        blocks = [e.block_number for e in self._events]
        return {
            "total_events": self.total,
            "unique_event_types": len(self.event_names()),
            "event_frequency": self.event_frequency(),
            "block_range": (min(blocks), max(blocks)) if blocks else (0, 0),
        }
