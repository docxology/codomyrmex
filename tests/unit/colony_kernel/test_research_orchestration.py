"""Functional tests for dependency-aware research orchestration."""

import pytest

from codomyrmex.colony_kernel.research.orchestration import (
    ResearchProgramOrchestrator,
    ResearchTrack,
    TrackStatus,
)


def test_program_runs_in_dependency_order() -> None:
    events: list[str] = []
    program = ResearchProgramOrchestrator(
        [
            ResearchTrack("R2", lambda: events.append("R2") or "receipt"),
            ResearchTrack("R4", lambda: events.append("R4") or "calibration", ("R2",)),
            ResearchTrack("R3", lambda: events.append("R3") or "benchmark", ("R2",)),
        ]
    )

    report = program.run()

    assert events == ["R2", "R3", "R4"]
    assert report.succeeded
    assert report.by_track()["R4"].output == "calibration"


def test_failure_is_retained_and_blocks_dependants() -> None:
    def fail() -> None:
        raise RuntimeError("external witness unavailable")

    program = ResearchProgramOrchestrator(
        [
            ResearchTrack("R2", fail),
            ResearchTrack("R4", lambda: "must not run", ("R2",)),
        ]
    )

    report = program.run()

    assert not report.succeeded
    assert report.by_track()["R2"].status is TrackStatus.FAILED
    assert report.by_track()["R2"].reason == "RuntimeError: external witness unavailable"
    assert report.by_track()["R4"].status is TrackStatus.BLOCKED


@pytest.mark.parametrize(
    ("tracks", "message"),
    [
        ([ResearchTrack("R2", lambda: None, ("R1",))], "Unknown"),
        (
            [
                ResearchTrack("R2", lambda: None, ("R3",)),
                ResearchTrack("R3", lambda: None, ("R2",)),
            ],
            "cycle",
        ),
    ],
)
def test_program_rejects_invalid_dependency_graphs(tracks, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        ResearchProgramOrchestrator(tracks)
