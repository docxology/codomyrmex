"""Real temporary CLI executables; no Fabric account or provider requests."""

import subprocess
from pathlib import Path

import pytest

from codomyrmex.llm.fabric.fabric_manager import FabricManager
from codomyrmex.llm.fabric.fabric_orchestrator import FabricOrchestrator

pytestmark = pytest.mark.unit


def executable(tmp_path: Path, listing: str, version_exit: int = 0) -> str:
    path = tmp_path / "fabric local"
    path.write_text(
        "#!/bin/sh\n"
        'case "$1" in\n'
        f'--version) printf "local-version\\n"; exit {version_exit} ;;\n'
        f"--listpatterns) {listing} ;;\n"
        "--pattern) /bin/cat ;;\n"
        "*) exit 99 ;;\n"
        "esac\n"
    )
    path.chmod(0o700)
    return str(path)


def test_successful_listing_and_local_execution(tmp_path: Path) -> None:
    binary = executable(
        tmp_path,
        'printf "  Available patterns:\\n\\n alpha \\nbeta\\n"; exit 0',
    )
    manager = FabricManager(binary)
    assert manager.is_available()
    assert manager.list_patterns() == ["alpha", "beta"]
    result = manager.run_pattern("alpha", "local-only input")
    assert result["success"] is True
    assert result["output"] == "local-only input"
    assert result["error"] == ""
    assert manager.get_results_history() == [result]


def test_nonzero_listing_raises_subprocess_error(tmp_path: Path) -> None:
    binary = executable(
        tmp_path, 'printf "partial-output"; printf "local-error" >&2; exit 17'
    )
    manager = FabricManager(binary)
    with pytest.raises(subprocess.CalledProcessError) as caught:
        manager.list_patterns()
    assert caught.value.returncode == 17
    assert caught.value.cmd == [binary, "--listpatterns"]
    assert caught.value.stdout == "partial-output"
    assert caught.value.stderr == "local-error"
    # The public orchestrator forwards the same explicit error contract.
    with pytest.raises(subprocess.CalledProcessError):
        FabricOrchestrator(binary).list_patterns()


def test_successful_empty_listing_returns_list(tmp_path: Path) -> None:
    manager = FabricManager(executable(tmp_path, 'printf "Available patterns:\\n"'))
    assert manager.list_patterns() == []


def test_version_failure_preserves_unavailable_contract(tmp_path: Path) -> None:
    manager = FabricManager(executable(tmp_path, "exit 99", version_exit=7))
    assert manager.is_available() is False
    assert manager.list_patterns() == []
    result = manager.run_pattern("alpha", "input")
    assert result["success"] is False
    assert result["error"] == "Fabric not available"
    assert manager.get_results_history() == []
