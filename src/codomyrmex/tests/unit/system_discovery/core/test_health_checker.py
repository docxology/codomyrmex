import sys
from pathlib import Path

import pytest

from codomyrmex.system_discovery.core.health_checker import SystemHealthChecker


@pytest.fixture
def health_checker(tmp_path: Path) -> SystemHealthChecker:
    """Provide a SystemHealthChecker instance with a temporary directory structure."""
    project_root = tmp_path / "project"
    project_root.mkdir()

    src_path = project_root / "src"
    src_path.mkdir()

    testing_path = project_root / "tests"
    testing_path.mkdir()

    # Create fake venv directory so venv_exists returns True
    venv_path = project_root / ".venv"
    venv_path.mkdir()

    return SystemHealthChecker(
        project_root=project_root, src_path=src_path, testing_path=testing_path
    )


def test_get_system_status_dict(health_checker: SystemHealthChecker) -> None:
    """Test get_system_status_dict returns correct structure and types."""
    status = health_checker.get_system_status_dict()

    # Verify main keys exist
    assert "python" in status
    assert "project" in status
    assert "dependencies" in status
    assert "git" in status

    # Check Python status dictionary
    assert "version" in status["python"]
    assert status["python"]["version"] == sys.version.split()[0]

    assert "executable" in status["python"]
    assert status["python"]["executable"] == sys.executable

    assert "virtual_env" in status["python"]
    assert isinstance(status["python"]["virtual_env"], bool)

    # Check Project status dictionary
    assert "src_exists" in status["project"]
    assert status["project"]["src_exists"] is True

    assert "tests_exist" in status["project"]
    assert status["project"]["tests_exist"] is True

    assert "venv_exists" in status["project"]
    assert status["project"]["venv_exists"] is True

    # Check dependencies dictionary structure
    expected_deps = [
        "python-dotenv",
        "cased-kit",
        "openai",
        "anthropic",
        "matplotlib",
        "numpy",
        "pytest",
    ]
    for dep in expected_deps:
        assert dep in status["dependencies"]
        assert isinstance(status["dependencies"][dep], bool)

    # Check git dictionary
    assert "is_repo" in status["git"]
    assert isinstance(status["git"]["is_repo"], bool)

    # The tmp_path is not a git repo, so is_repo should be False
    assert status["git"]["is_repo"] is False
    # When is_repo is False, these keys aren't set
    assert "branch" not in status["git"]
    assert "clean" not in status["git"]


def test_get_system_status_dict_git_repo(
    health_checker: SystemHealthChecker, tmp_path: Path
) -> None:
    """Test git-related keys when executed within a git repository."""
    import subprocess

    # Initialize a simple git repository in the tmp_path/project
    project_root = health_checker.project_root
    subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"], cwd=project_root, check=True
    )
    subprocess.run(["git", "config", "user.name", "test"], cwd=project_root, check=True)

    # Needs at least one commit for branch to show up
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "Initial commit"],
        cwd=project_root,
        check=True,
        capture_output=True,
    )

    # Switch to main branch to have deterministic output
    subprocess.run(
        ["git", "checkout", "-b", "main"],
        cwd=project_root,
        check=False,
        capture_output=True,
    )

    status = health_checker.get_system_status_dict()

    assert status["git"]["is_repo"] is True
    assert status["git"]["branch"] == "main"
    assert status["git"]["clean"] is True

    # Introduce an uncommitted change
    (project_root / "untracked.txt").write_text("hello")
    status = health_checker.get_system_status_dict()
    assert status["git"]["clean"] is False
