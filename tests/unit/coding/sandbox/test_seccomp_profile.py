"""Contract tests for the Docker sandbox seccomp profile.

The profile is an allowlist (``defaultAction: SCMP_ACT_ERRNO``). Modern
container runtimes and C libraries issue syscalls that older allowlists
omit; when they are denied, ``runc`` cannot start the container at all.
Regression: runc >= 1.2 calls ``statx(STATX_MNT_ID)`` while re-opening the
exec FIFO after the filter is installed, so every sandboxed run failed with
``could not get mount id: operation not permitted`` (exit 127) on current
GitHub runners.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from codomyrmex.coding.sandbox import resource_limits

PROFILE_PATH = Path(resource_limits.__file__).parent / "seccomp_profile.json"

# Syscalls required by runc's post-filter init and glibc >= 2.34 startup.
RUNTIME_REQUIRED = {
    "arch_prctl",  # x86_64 TLS setup in every dynamically linked process
    "close_range",  # runc closes inherited fds before exec
    "execve",
    "faccessat2",  # glibc access()/faccessat() since 2.33
    "futex",
    "newfstatat",
    "pipe2",  # subprocess / multiprocessing pipes
    "rseq",  # glibc 2.35 restartable sequences registration
    "statx",  # runc safe /proc handling (mount-id checks)
}

# Syscalls that must stay blocked for an untrusted-code sandbox.
MUST_BLOCK = {
    "bpf",
    "init_module",
    "finit_module",
    "kexec_load",
    "mount",
    "umount2",
    "pivot_root",
    "ptrace",
    "reboot",
    "setns",
    "unshare",
    "keyctl",
    "add_key",
    "open_by_handle_at",
}


@pytest.fixture(scope="module")
def profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def _allowed(profile: dict) -> set[str]:
    return {
        name
        for rule in profile["syscalls"]
        if rule.get("action") == "SCMP_ACT_ALLOW"
        for name in rule["names"]
    }


@pytest.mark.unit
def test_profile_is_default_deny(profile: dict) -> None:
    assert profile["defaultAction"] == "SCMP_ACT_ERRNO"
    assert "SCMP_ARCH_X86_64" in profile["architectures"]


@pytest.mark.unit
def test_runtime_required_syscalls_are_allowed(profile: dict) -> None:
    missing = RUNTIME_REQUIRED - _allowed(profile)
    assert not missing, f"seccomp profile blocks runtime-required syscalls: {missing}"


@pytest.mark.unit
def test_dangerous_syscalls_remain_blocked(profile: dict) -> None:
    leaked = MUST_BLOCK & _allowed(profile)
    assert not leaked, f"seccomp profile allows dangerous syscalls: {leaked}"


@pytest.mark.unit
def test_clone3_returns_enosys_so_glibc_falls_back(profile: dict) -> None:
    rules = [r for r in profile["syscalls"] if "clone3" in r["names"]]
    assert len(rules) == 1
    assert rules[0]["action"] == "SCMP_ACT_ERRNO"
    assert rules[0]["errnoRet"] == 38  # ENOSYS


@pytest.mark.unit
def test_rule_names_are_unique_and_sorted(profile: dict) -> None:
    names = profile["syscalls"][0]["names"]
    assert names == sorted(set(names))


@pytest.mark.unit
def test_default_docker_args_reference_profile() -> None:
    assert (
        f"--security-opt=seccomp={PROFILE_PATH}" in resource_limits.DEFAULT_DOCKER_ARGS
    )


def _docker_can_run(image: str) -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        info = subprocess.run(
            ["docker", "image", "inspect", image],
            capture_output=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return info.returncode == 0


@pytest.mark.integration
@pytest.mark.requires_docker
@pytest.mark.skipif(
    not _docker_can_run("python:3.9-slim"),
    reason="requires a running Docker daemon with python:3.9-slim pulled",
)
def test_profile_starts_real_container_with_threads_and_subprocess() -> None:
    code = (
        "import subprocess, sys, threading\n"
        "t = threading.Thread(target=print, args=('thread-ok',)); t.start(); t.join()\n"
        "r = subprocess.run([sys.executable, '-c', 'print(\"child-ok\")'],"
        " capture_output=True, text=True)\n"
        "print(r.stdout.strip())\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "code.py"
        script.write_text(code, encoding="utf-8")
        Path(tmp).chmod(0o755)
        script.chmod(0o644)
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                *resource_limits.DEFAULT_DOCKER_ARGS,
                f"-v={tmp}:/sandbox:ro",
                "-w=/sandbox",
                "python:3.9-slim",
                "python",
                "code.py",
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["thread-ok", "child-ok"]
