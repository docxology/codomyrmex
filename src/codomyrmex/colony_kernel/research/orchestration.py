"""Dependency-aware orchestration for Colony Kernel research tracks."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class TrackStatus(StrEnum):
    """Terminal state of one attempted research track."""

    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ResearchTrack:
    """Executable track and the track identifiers whose evidence it requires."""

    track_id: str
    runner: Callable[[], Any]
    dependencies: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.track_id.strip():
            raise ValueError("track_id must be non-empty")
        if self.track_id in self.dependencies:
            raise ValueError(f"Track {self.track_id} cannot depend on itself")


@dataclass(frozen=True)
class TrackResult:
    """Retained outcome for one research track."""

    track_id: str
    status: TrackStatus
    output: Any = None
    reason: str | None = None


@dataclass(frozen=True)
class ResearchProgramReport:
    """Ordered, lossless record of a research program execution."""

    results: tuple[TrackResult, ...]

    @property
    def succeeded(self) -> bool:
        return bool(self.results) and all(
            result.status is TrackStatus.COMPLETED for result in self.results
        )

    def by_track(self) -> dict[str, TrackResult]:
        return {result.track_id: result for result in self.results}


class ResearchProgramOrchestrator:
    """Execute a validated track DAG while preserving failures and blocked work."""

    def __init__(self, tracks: Iterable[ResearchTrack]) -> None:
        track_list = list(tracks)
        self._tracks = {track.track_id: track for track in track_list}
        if len(self._tracks) != len(track_list):
            raise ValueError("Research track identifiers must be unique")
        self._order = self._topological_order()

    def _topological_order(self) -> tuple[str, ...]:
        unknown = {
            dependency
            for track in self._tracks.values()
            for dependency in track.dependencies
            if dependency not in self._tracks
        }
        if unknown:
            raise ValueError(f"Unknown research dependencies: {', '.join(sorted(unknown))}")

        remaining = set(self._tracks)
        ordered: list[str] = []
        while remaining:
            ready = sorted(
                track_id
                for track_id in remaining
                if set(self._tracks[track_id].dependencies) <= set(ordered)
            )
            if not ready:
                raise ValueError("Research track dependencies contain a cycle")
            ordered.extend(ready)
            remaining.difference_update(ready)
        return tuple(ordered)

    def run(self) -> ResearchProgramReport:
        """Run each track once; failed prerequisites block their dependants."""
        results: list[TrackResult] = []
        by_track: dict[str, TrackResult] = {}
        for track_id in self._order:
            track = self._tracks[track_id]
            blockers = [
                dependency
                for dependency in track.dependencies
                if by_track[dependency].status is not TrackStatus.COMPLETED
            ]
            if blockers:
                result = TrackResult(
                    track_id,
                    TrackStatus.BLOCKED,
                    reason=f"Blocked by incomplete dependencies: {', '.join(blockers)}",
                )
            else:
                try:
                    result = TrackResult(
                        track_id, TrackStatus.COMPLETED, output=track.runner()
                    )
                except Exception as exc:  # research failures are retained as evidence
                    result = TrackResult(
                        track_id,
                        TrackStatus.FAILED,
                        reason=f"{type(exc).__name__}: {exc}",
                    )
            results.append(result)
            by_track[track_id] = result
        return ResearchProgramReport(tuple(results))


__all__ = [
    "ResearchProgramOrchestrator",
    "ResearchProgramReport",
    "ResearchTrack",
    "TrackResult",
    "TrackStatus",
]
