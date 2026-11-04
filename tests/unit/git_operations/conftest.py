"""Pytest configuration and shared fixtures for git_operations tests."""

import os
import shutil
import subprocess
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from tests.support.git_temp_repository import assert_contained, initialize_repository


@pytest.fixture(autouse=True)
def contained_process_state() -> Generator[None, None, None]:
    """Fail the test that leaves the process outside its own temporary tree.

    The library's mutating helpers fall back to ``os.getcwd()`` when they are given no
    repository path. A test that changes the working directory and does not restore it
    can therefore make a later test act on whichever repository the process happens to
    be standing in, so the trip out of temporary space is treated as a failure.
    """
    before = Path.cwd()
    yield
    after = Path.cwd()
    if after != before:
        assert_contained(after, tempfile.gettempdir())
        os.chdir(before)


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

    initialize_repository(repo_path, initial_commit=True, root=temp_dir)

    # Ensure we are on 'main' regardless of system default
    subprocess.run(
        ["git", "branch", "-m", "main"], cwd=repo_path, capture_output=True, check=False
    )

    return repo_path

    # Cleanup is handled by temp_dir fixture


@pytest.fixture
def temp_git_repo_no_commit(temp_dir: str) -> Generator[str, None, None]:
    """Create a temporary Git repository without initial commit."""
    repo_path = os.path.join(temp_dir, "test_repo_no_commit")
    os.makedirs(repo_path, exist_ok=True)

    initialize_repository(repo_path, initial_commit=False, root=temp_dir)

    return repo_path

    # Cleanup is handled by temp_dir fixture


@pytest.fixture
def sample_file(temp_git_repo: str) -> Generator[str, None, None]:
    """Create a sample file in the test repository."""
    file_path = os.path.join(temp_git_repo, "test_file.txt")
    with open(file_path, "w") as f:
        f.write("Test content\n")

    return file_path
