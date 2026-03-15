"""Integration tests for Hermes gateway lifecycle and PID management."""

import multiprocessing
import time
from pathlib import Path

import pytest

from codomyrmex.agents.hermes.gateway.server import GatewayRunner


def _run_gateway(home_dir: str, replace: bool) -> None:
    """Helper to run the gateway in a subprocess to test PID behavior."""
    runner = GatewayRunner(replace=replace, home_dir=home_dir)
    runner.run()


@pytest.fixture
def temp_home(tmp_path: Path) -> str:
    """Temporary standard HERMES_HOME."""
    return str(tmp_path / "hermes_test")


def test_gateway_startup_writes_pid(temp_home: str) -> None:
    """Ensure starting a gateway writes the correct PID."""
    home = Path(temp_home)
    home.mkdir(parents=True, exist_ok=True)

    proc = multiprocessing.Process(target=_run_gateway, args=(temp_home, False))
    proc.start()

    # Wait for PID file
    for _ in range(20):
        if (home / "gateway.pid").exists():
            break
        time.sleep(0.1)

    assert (home / "gateway.pid").exists()

    pid_str = (home / "gateway.pid").read_text().strip()
    assert pid_str == str(proc.pid)

    # Cleanup
    proc.terminate()
    proc.join(timeout=2.0)
    if proc.is_alive():
        proc.kill()


def test_gateway_refuses_when_active_without_replace(temp_home: str) -> None:
    """Ensure a second gateway refuses to start if the first is alive and `--replace` is False."""
    home = Path(temp_home)
    home.mkdir(parents=True, exist_ok=True)

    p1 = multiprocessing.Process(target=_run_gateway, args=(temp_home, False))
    p1.start()

    # Wait for first to establish
    for _ in range(20):
        if (home / "gateway.pid").exists():
            break
        time.sleep(0.1)

    assert p1.pid is not None

    p2 = multiprocessing.Process(target=_run_gateway, args=(temp_home, False))
    p2.start()
    p2.join(timeout=2.0)

    # Failed to start natively without crashing the test runner, exits cleanly with code 0 per docs
    assert p2.exitcode == 0

    # Original should be untouched
    assert p1.is_alive()
    assert (home / "gateway.pid").read_text().strip() == str(p1.pid)

    p1.terminate()
    p1.join()


def test_gateway_replace_kills_old_pid(temp_home: str) -> None:
    """Ensure `--replace` flag terminates the old PID and claims ownership."""
    home = Path(temp_home)
    home.mkdir(parents=True, exist_ok=True)

    p1 = multiprocessing.Process(target=_run_gateway, args=(temp_home, False))
    p1.start()

    for _ in range(20):
        if (home / "gateway.pid").exists():
            break
        time.sleep(0.1)

    original_pid = p1.pid

    p2 = multiprocessing.Process(target=_run_gateway, args=(temp_home, True))
    p2.start()

    # Wait for takeover
    for _ in range(20):
        if not (home / "gateway.pid").exists():
            time.sleep(0.1)
            continue
        pid_str = (home / "gateway.pid").read_text().strip()
        if pid_str == str(p2.pid):
            break
        time.sleep(0.1)

    assert (home / "gateway.pid").read_text().strip() == str(p2.pid)

    p1.join(timeout=2.0)
    # the old process should be dead because the new one killed it via SIGTERM
    assert not p1.is_alive()

    p2.terminate()
    p2.join()
