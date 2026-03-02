"""Memory profiler for leak detection.

Tracks object allocation counts and memory deltas across
execution phases to detect leaks.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class MemorySnapshot:
    """Memory state at a point in time.

    Attributes:
        label: Snapshot label.
        timestamp: When taken.
        object_count: Total tracked objects.
        tracked_types: Object count per type.
    """

    label: str
    timestamp: float = field(default_factory=time.time)
    object_count: int = 0
    tracked_types: dict[str, int] = field(default_factory=dict)


@dataclass
class MemoryDelta:
    """Difference between two memory snapshots.

    Attributes:
        from_label: Starting snapshot.
        to_label: Ending snapshot.
        object_delta: Change in total object count.
        type_deltas: Per-type changes.
        leak_suspected: Whether growth suggests a leak.
    """

    from_label: str
    to_label: str
    object_delta: int = 0
    type_deltas: dict[str, int] = field(default_factory=dict)
    leak_suspected: bool = False


class MemoryProfiler:
    """Track memory across execution phases.

    Example::

        profiler = MemoryProfiler()
        profiler.snapshot("before")
        do_work()
        profiler.snapshot("after")
        delta = profiler.diff("before", "after")
        assert not delta.leak_suspected
    """

    def __init__(self, leak_threshold: int = 1000) -> None:
        self._snapshots: dict[str, MemorySnapshot] = {}
        self._leak_threshold = leak_threshold

    @property
    def snapshot_count(self) -> int:
        return len(self._snapshots)

    def snapshot(self, label: str) -> MemorySnapshot:
        """Take a memory snapshot.

        Args:
            label: Snapshot identifier.

        Returns:
            The captured snapshot.
        """
        # Use sys.getrefcount and gc-style counting
        import gc
        gc.collect()

        type_counts: dict[str, int] = {}
        total = 0
        for obj in gc.get_objects():
            t = type(obj).__name__
            type_counts[t] = type_counts.get(t, 0) + 1
            total += 1

        snap = MemorySnapshot(
            label=label,
            object_count=total,
            tracked_types=dict(sorted(type_counts.items(), key=lambda x: -x[1])[:20]),
        )
        self._snapshots[label] = snap
        return snap

    def snapshot_lightweight(self, label: str, tracked_count: int = 0) -> MemorySnapshot:
        """Take a lightweight snapshot without gc traversal.

        Args:
            label: Snapshot label.
            tracked_count: Manually provided object count.

        Returns:
            The snapshot.
        """
        snap = MemorySnapshot(
            label=label,
            object_count=tracked_count,
        )
        self._snapshots[label] = snap
        return snap

    def diff(self, label_a: str, label_b: str) -> MemoryDelta:
        """Compute difference between two snapshots.

        Args:
            label_a: First snapshot.
            label_b: Second snapshot.

        Returns:
            MemoryDelta with changes.
        """
        a = self._snapshots.get(label_a)
        b = self._snapshots.get(label_b)
        if a is None or b is None:
            return MemoryDelta(from_label=label_a, to_label=label_b)

        object_delta = b.object_count - a.object_count

        type_deltas: dict[str, int] = {}
        all_types = set(a.tracked_types) | set(b.tracked_types)
        for t in all_types:
            delta = b.tracked_types.get(t, 0) - a.tracked_types.get(t, 0)
            if delta != 0:
                type_deltas[t] = delta

        return MemoryDelta(
            from_label=label_a,
            to_label=label_b,
            object_delta=object_delta,
            type_deltas=type_deltas,
            leak_suspected=object_delta > self._leak_threshold,
        )

    def get_snapshot(self, label: str) -> MemorySnapshot | None:
        return self._snapshots.get(label)


__all__ = ["MemoryDelta", "MemoryProfiler", "MemorySnapshot"]
