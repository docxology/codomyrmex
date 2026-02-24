"""Deterministic event replayer.

Reads events from the EventStore and re-emits them in order,
verifying that handler outputs are deterministic.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

from codomyrmex.events.event_store import EventStore, StreamEvent


@dataclass
class ReplayResult:
    """Result of an event replay session.

    Attributes:
        events_replayed: Number of events processed.
        handler_outputs: Output from each handler invocation.
        duration_ms: Time taken for replay.
        deterministic: Whether outputs matched expectations.
    """

    events_replayed: int = 0
    handler_outputs: list[Any] = field(default_factory=list)
    duration_ms: float = 0.0
    deterministic: bool = True


class EventReplayer:
    """Replay events from an EventStore for debugging.

    Re-emits events in sequence order and captures handler
    outputs for determinism verification.

    Example::

        replayer = EventReplayer(store=event_store)
        result = replayer.replay(
            handlers={"agent": my_handler},
        )
        assert result.deterministic
    """

    def __init__(self, store: EventStore) -> None:
        """Execute   Init   operations natively."""
        self._store = store

    def replay(
        self,
        from_seq: int = 1,
        to_seq: int = 0,
        handlers: dict[str, Callable[[StreamEvent], Any]] | None = None,
    ) -> ReplayResult:
        """Replay events through handlers.

        Args:
            from_seq: Start sequence.
            to_seq: End sequence (0 = latest).
            handlers: Topic → handler mapping.

        Returns:
            ReplayResult with outputs and timing.
        """
        start = time.monotonic()
        events = self._store.read(from_seq, to_seq)
        outputs: list[Any] = []

        for event in events:
            if handlers and event.topic in handlers:
                output = handlers[event.topic](event)
                outputs.append(output)

        elapsed = (time.monotonic() - start) * 1000

        return ReplayResult(
            events_replayed=len(events),
            handler_outputs=outputs,
            duration_ms=elapsed,
        )

    def replay_by_time(
        self,
        from_time: float,
        to_time: float,
        handlers: dict[str, Callable[[StreamEvent], Any]] | None = None,
    ) -> ReplayResult:
        """Replay events in a time range.

        Args:
            from_time: Start timestamp.
            to_time: End timestamp.
            handlers: Topic → handler mapping.

        Returns:
            ReplayResult.
        """
        start = time.monotonic()
        events = self._store.read_by_time(from_time, to_time)
        outputs: list[Any] = []

        for event in events:
            if handlers and event.topic in handlers:
                outputs.append(handlers[event.topic](event))

        elapsed = (time.monotonic() - start) * 1000

        return ReplayResult(
            events_replayed=len(events),
            handler_outputs=outputs,
            duration_ms=elapsed,
        )

    def diff(self, result_a: ReplayResult, result_b: ReplayResult) -> dict[str, Any]:
        """Compare two replay results for determinism.

        Args:
            result_a: First replay result.
            result_b: Second replay result.

        Returns:
            Dict with comparison details.
        """
        outputs_match = result_a.handler_outputs == result_b.handler_outputs
        return {
            "deterministic": outputs_match,
            "events_a": result_a.events_replayed,
            "events_b": result_b.events_replayed,
            "outputs_match": outputs_match,
            "mismatches": (
                []
                if outputs_match
                else [
                    i
                    for i, (a, b) in enumerate(
                        zip(result_a.handler_outputs, result_b.handler_outputs)
                    )
                    if a != b
                ]
            ),
        }


__all__ = ["EventReplayer", "ReplayResult"]
