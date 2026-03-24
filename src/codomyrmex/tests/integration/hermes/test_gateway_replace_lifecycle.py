import os
import subprocess
import sys
import time
from pathlib import Path

import pytest


def _run_gateway_process(home_dir: str, replace: bool) -> subprocess.Popen:
    """Helper to run the gateway in a subprocess to test PID behavior."""
    script = f"""
import sys
from codomyrmex.agents.hermes.gateway.server import GatewayRunner
runner = GatewayRunner(replace={replace}, home_dir="{home_dir}")
runner.run()
"""
    env = os.environ.copy()
    _root = str(Path(__file__).parent.parent.parent.parent.parent.resolve())
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{_root}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = _root
    return subprocess.Popen([sys.executable, "-c", script], env=env)


@pytest.fixture
def temp_home(tmp_path: Path) -> str:
    """Temporary standard HERMES_HOME."""
    return str(tmp_path / "hermes_test")


def test_gateway_startup_writes_pid(temp_home: str) -> None:
    """Ensure starting a gateway writes the correct PID."""
    home = Path(temp_home)
    home.mkdir(parents=True, exist_ok=True)

    proc = _run_gateway_process(temp_home, False)

    # Wait for PID file
    for _ in range(100):
        if (home / "gateway.pid").exists():
            break
        time.sleep(0.1)

    assert (home / "gateway.pid").exists()

    pid_str = (home / "gateway.pid").read_text().strip()
    assert pid_str == str(proc.pid)

    # Cleanup
    proc.terminate()
    try:
        proc.wait(timeout=2.0)
    except subprocess.TimeoutExpired:
        proc.kill()


def test_gateway_refuses_when_active_without_replace(temp_home: str) -> None:
    """Ensure a second gateway refuses to start if the first is alive and `--replace` is False."""
    home = Path(temp_home)
    home.mkdir(parents=True, exist_ok=True)

    p1 = _run_gateway_process(temp_home, False)

    # Wait for first to establish
    for _ in range(100):
        if (home / "gateway.pid").exists():
            break
        time.sleep(0.1)

    assert p1.pid is not None

    p2 = _run_gateway_process(temp_home, False)
    p2.wait(timeout=5.0)

    # Failed to start natively without crashing the test runner, exits cleanly with code 0 per docs
    assert p2.returncode == 0

    # Original should be untouched
    assert p1.poll() is None
    assert (home / "gateway.pid").read_text().strip() == str(p1.pid)

    p1.terminate()
    p1.wait()


def test_gateway_replace_kills_old_pid(temp_home: str) -> None:
    """Ensure `--replace` flag terminates the old PID and claims ownership."""
    home = Path(temp_home)
    home.mkdir(parents=True, exist_ok=True)

    p1 = _run_gateway_process(temp_home, False)

    for _ in range(100):
        if (home / "gateway.pid").exists():
            break
        time.sleep(0.1)


    p2 = _run_gateway_process(temp_home, True)

    # Wait for takeover
    for _ in range(100):
        if not (home / "gateway.pid").exists():
            time.sleep(0.1)
            continue
        pid_str = (home / "gateway.pid").read_text().strip()
        if pid_str == str(p2.pid):
            break
        time.sleep(0.1)

    assert (home / "gateway.pid").read_text().strip() == str(p2.pid)

    try:
        p1.wait(timeout=2.0)
    except subprocess.TimeoutExpired:
        pass

    # the old process should be dead because the new one killed it via SIGTERM
    assert p1.poll() is not None

    p2.terminate()
    p2.wait()
