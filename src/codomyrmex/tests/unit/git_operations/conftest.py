from pathlib import Path
from typing import Generator
import os
import shutil
import tempfile

import pytest

from codomyrmex.git_operations import initialize_git_repository




























































"""
"""Core functionality module

This module provides conftest functionality including:
- 4 functions: temp_dir, temp_git_repo, temp_git_repo_no_commit...
- 0 classes: 

Usage:
    # Example usage here
"""
Pytest configuration and shared fixtures for git_operations tests.
"""





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
    
    yield repo_path
    
    # Cleanup is handled by temp_dir fixture


@pytest.fixture
def temp_git_repo_no_commit(temp_dir: str) -> Generator[str, None, None]:
    """Create a temporary Git repository without initial commit."""
    repo_path = os.path.join(temp_dir, "test_repo_no_commit")
    os.makedirs(repo_path, exist_ok=True)
    
    # Initialize Git repository without initial commit
    initialize_git_repository(repo_path, initial_commit=False)
    
    yield repo_path
    
    # Cleanup is handled by temp_dir fixture


@pytest.fixture
def sample_file(temp_git_repo: str) -> Generator[str, None, None]:
    """Create a sample file in the test repository."""
    file_path = os.path.join(temp_git_repo, "test_file.txt")
    with open(file_path, "w") as f:
        f.write("Test content\n")
    
    yield file_path

