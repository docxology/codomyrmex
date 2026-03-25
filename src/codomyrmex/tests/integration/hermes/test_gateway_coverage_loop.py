"""Tests for _run_coverage_loop edge cases in HermesClient.

Validates that the autonomous coverage loop handles:
- Max turns exhaustion
- Success on retry turn
- Timeout handling
- Missing target paths (error before pytest)

Zero-Mock Policy: All subprocess results are real ``subprocess.CompletedProcess``
objects. Behavior injection uses real subclasses and monkeypatch, not MagicMock.
"""

import subprocess
from pathlib import Path

import pytest

from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.hermes.hermes_client import HermesClient


@pytest.fixture
def temp_db(tmp_path: Path):
    db_path = tmp_path / "test_coverage_loop_sessions.db"
    yield db_path
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def coverage_target_path(tmp_path: Path) -> str:
    """Real path required: _run_coverage_loop rejects missing targets before pytest."""
    path = tmp_path / "target_test.py"
    path.write_text("# placeholder test target\n", encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------------
# Real HermesClient subclasses — zero mocks
# ---------------------------------------------------------------------------


class CoverageLoopClient(HermesClient):
    """Real HermesClient subclass for coverage loop tests.

    Always returns a successful repair response so that test isolation
    depends only on the subprocess.run outcome that we control.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.execute_call_count = 0

    def execute(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        self.execute_call_count += 1
        return AgentResponse(
            content="Fixed the issue.",
            error=None,
            metadata={"exit_code": 0},
        )


class FailingCoverageClient(HermesClient):
    """Real HermesClient subclass where execute() always returns failure."""

    def execute(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        return AgentResponse(
            content="",
            error="Repair agent crashed",
            metadata={"exit_code": 1},
        )


# ---------------------------------------------------------------------------
# Helper: build a real CompletedProcess result
# ---------------------------------------------------------------------------


def _completed(
    returncode: int, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=["pytest"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_coverage_loop_max_turns_exhaustion(
    temp_db: Path,
    coverage_target_path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that coverage loop stops at max_turns when tests always fail."""
    client = CoverageLoopClient(
        config={
            "hermes_backend": "ollama",
            "hermes_session_db": str(temp_db),
        }
    )

    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: _completed(
            1, "FAILED test_foo.py::test_bar - AssertionError"
        ),
    )
    result = client._run_coverage_loop(coverage_target_path, max_turns=3)

    assert result["status"] == "failed"
    assert "3 turns" in result["message"]
    assert "trace" in result


def test_coverage_loop_success_on_second_turn(
    temp_db: Path,
    coverage_target_path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that coverage loop succeeds when tests pass on turn 2."""
    client = CoverageLoopClient(
        config={
            "hermes_backend": "ollama",
            "hermes_session_db": str(temp_db),
        }
    )

    call_count = 0

    def real_subprocess_run(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _completed(1, "FAILED test_foo.py")
        return _completed(0, "1 passed")

    monkeypatch.setattr("subprocess.run", real_subprocess_run)
    result = client._run_coverage_loop(coverage_target_path, max_turns=5)

    assert result["status"] == "success"
    assert result["turns"] == 1
    assert "1 passed" in result["output"]


def test_coverage_loop_timeout_handling(
    temp_db: Path,
    coverage_target_path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that coverage loop handles subprocess timeout gracefully."""
    client = CoverageLoopClient(
        config={
            "hermes_backend": "ollama",
            "hermes_session_db": str(temp_db),
        }
    )

    def timeout_run(*args, **kwargs):
        raise subprocess.TimeoutExpired("pytest", 120)

    monkeypatch.setattr("subprocess.run", timeout_run)
    result = client._run_coverage_loop(coverage_target_path, max_turns=2)

    # Should return error status due to unhandled exception
    assert result["status"] in ("error", "failed")


def test_coverage_loop_empty_target(
    temp_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing target path returns error before pytest; subprocess is never run."""
    client = CoverageLoopClient(
        config={
            "hermes_backend": "ollama",
            "hermes_session_db": str(temp_db),
        }
    )

    ran: list[bool] = []

    def _track_run(*args, **kwargs):
        ran.append(True)
        return _completed(0, "ok")

    monkeypatch.setattr("subprocess.run", _track_run)
    result = client._run_coverage_loop("/nonexistent/path_xyz_12345.py", max_turns=1)

    assert result["status"] == "error"
    assert "does not exist" in result["message"]
    assert ran == []


def test_coverage_loop_repair_agent_failure(
    temp_db: Path,
    coverage_target_path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test coverage loop when repair agent itself fails.

    Uses FailingCoverageClient — a real subclass with no mocks.
    """
    client = FailingCoverageClient(
        config={
            "hermes_backend": "ollama",
            "hermes_session_db": str(temp_db),
        }
    )

    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: _completed(1, "FAILED test_foo.py"),
    )
    result = client._run_coverage_loop(coverage_target_path, max_turns=3)

    assert result["status"] == "error"
    assert "Repair agent failed" in result["message"]


def test_coverage_loop_zero_max_turns(
    temp_db: Path,
    coverage_target_path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test coverage loop with max_turns=0 returns immediately."""
    client = CoverageLoopClient(
        config={
            "hermes_backend": "ollama",
            "hermes_session_db": str(temp_db),
        }
    )

    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: _completed(1, "FAILED"),
    )
    result = client._run_coverage_loop(coverage_target_path, max_turns=0)

    assert result["status"] == "failed"
    assert "0 turns" in result["message"]
