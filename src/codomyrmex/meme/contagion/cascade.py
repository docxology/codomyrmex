"""Cascade detection utilities."""

from __future__ import annotations

from codomyrmex.meme.contagion.models import Cascade, CascadeType


class CascadeDetector:
    """Detect and classify information cascades from event streams."""

    def detect(self, events: list[dict]) -> list[Cascade]:
        """Detect cascades from a list of propagation events.

        Events should be dicts with at least:
        - 'meme_id': ID of the meme
        - 'node_id': Node adopting the meme
        - 'timestamp': Time of adoption
        - 'parent_id': Source of transmission (optional)

        Returns:
            List of detected Cascades.
        """
        # Group by meme_id
        grouped: dict[str, list[dict]] = {}
        for ev in events:
            mid = ev.get("meme_id")
            if mid:
                grouped.setdefault(mid, []).append(ev)

        cascades = []
        for mid, cluster in grouped.items():
            if not cluster:
                continue

            # Sort by time
            cluster.sort(key=lambda x: x.get("timestamp", 0))

            # Basic metrics
            start_time = cluster[0].get("timestamp", 0)
            end_time = cluster[-1].get("timestamp", 0)
            duration = end_time - start_time
            size = len(cluster)
            velocity = size / duration if duration > 0 else size

            # Classify
            c_type = CascadeType.ORGANIC
            if velocity > 10.0:  # Threshold heuristic
                c_type = CascadeType.VIRAL
            if size < 5:
                c_type = CascadeType.DAMPENED

            cascades.append(
                Cascade(
                    seed_id=mid,
                    size=size,
                    duration=duration,
                    velocity=velocity,
                    cascade_type=c_type,
                    participants=[ev.get("node_id", "") for ev in cluster],
                )
            )

        return cascades


def detect_cascades(events: list[dict]) -> list[Cascade]:
    """Convenience wrapper for CascadeDetector."""
    return CascadeDetector().detect(events)
