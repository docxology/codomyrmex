"""Default integration controls never use operator calendar credentials."""

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_calendar_auth(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> None:
    """Permit credentials only for an explicitly opted-in network test."""
    if (
        request.node.get_closest_marker("network") is not None
        and os.environ.get("CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS") == "1"
    ):
        return
    for name in ("GOOGLE_REFRESH_TOKEN", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(
        "GOOGLE_CALENDAR_TOKEN_FILE", str(tmp_path / "absent-token.json")
    )
    monkeypatch.setenv(
        "GOOGLE_APPLICATION_CREDENTIALS", str(tmp_path / "absent-adc.json")
    )
