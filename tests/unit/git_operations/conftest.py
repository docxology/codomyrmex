import os
import shutil
import tempfile
from collections.abc import Generator

import pytest

from codomyrmex.git_operations import initialize_git_repository

"""Pytest configuration and shared fixtures for git_operations tests.
"""


@pytest.fixture(autouse=True)
def deterministic_git_identity(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """Give real temporary repositories a CI-independent commit identity."""
    git_config = tmp_path_factory.mktemp("git-config") / "config"
    git_config.write_text(
        "[user]\n\tname = Codomyrmex Tests\n\temail = tests@codomyrmex.dev\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(git_config))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for variable in (
        "GIT_AUTHOR_NAME",
        "GIT_AUTHOR_EMAIL",
        "GIT_COMMITTER_NAME",
        "GIT_COMMITTER_EMAIL",
    ):
        monkeypatch.delenv(variable, raising=False)


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_git_repo(temp_dir: str) -> Generator[str, None, None]:
    """Create a temporary Git repository for tests."""
    repo_path = os.path.join(temp_dir, "test_repo")
    os.makedirs(repo_path, exist_ok=True)

    # Initialize Git repository
    initialize_git_repository(repo_path, initial_commit=True)

    # Ensure we are on 'main' regardless of system default
    import subprocess

    subprocess.run(
        ["git", "branch", "-m", "main"], cwd=repo_path, capture_output=True, check=False
    )

    return repo_path  # type: ignore

    # Cleanup is handled by temp_dir fixture


@pytest.fixture
def temp_git_repo_no_commit(temp_dir: str) -> Generator[str, None, None]:
    """Create a temporary Git repository without initial commit."""
    repo_path = os.path.join(temp_dir, "test_repo_no_commit")
    os.makedirs(repo_path, exist_ok=True)

    # Initialize Git repository without initial commit
    initialize_git_repository(repo_path, initial_commit=False)

    return repo_path  # type: ignore

    # Cleanup is handled by temp_dir fixture


@pytest.fixture
def sample_file(temp_git_repo: str) -> Generator[str, None, None]:
    """Create a sample file in the test repository."""
    file_path = os.path.join(temp_git_repo, "test_file.txt")
    with open(file_path, "w") as f:
        f.write("Test content\n")

    return file_path  # type: ignore
