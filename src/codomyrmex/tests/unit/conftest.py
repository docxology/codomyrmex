"""Shared pytest fixtures for unit tests.

Provides common fixtures used across per-module unit test directories.
Module-specific fixtures should live in their own conftest.py files.
"""

import os
from pathlib import Path

import pytest

# ═══════════════════════════════════════════════════════════════
# Service URL constants — override via env vars in CI/CD
# ═══════════════════════════════════════════════════════════════

#: Default Ollama server URL; override with OLLAMA_BASE_URL env var.
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

#: Default local container registry; override with CONTAINER_REGISTRY_URL env var.
CONTAINER_REGISTRY_URL: str = os.getenv("CONTAINER_REGISTRY_URL", "localhost:5000")


@pytest.fixture
def ollama_base_url() -> str:
    """Ollama server base URL, configurable via OLLAMA_BASE_URL env var."""
    return OLLAMA_BASE_URL


@pytest.fixture
def container_registry_url() -> str:
    """Local container registry URL, configurable via CONTAINER_REGISTRY_URL env var."""
    return CONTAINER_REGISTRY_URL

# ═══════════════════════════════════════════════════════════════
# Project paths
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def src_root() -> Path:
    """Path to the codomyrmex source root (src/codomyrmex/)."""
    return Path(__file__).parent.parent


@pytest.fixture
def project_root() -> Path:
    """Path to the repository root."""
    return Path(__file__).parent.parent.parent.parent


# ═══════════════════════════════════════════════════════════════
# Reusable temp-project scaffolds
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def minimal_project(tmp_path) -> Path:
    """Create a minimal Python project layout for testing.

    Returns a tmp_path containing:
        README.md, pyproject.toml, src/__init__.py, tests/__init__.py
    """
    (tmp_path / "README.md").write_text("# Test\n")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\n'
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("")
    return tmp_path


@pytest.fixture
def minimal_git_repo(tmp_path) -> Path:
    """Create a minimal git repository with one commit.

    Returns a tmp_path that is a valid git repository.
    """
    import subprocess

    subprocess.run(["git", "init", str(tmp_path)], capture_output=True, check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@test.com"],
        capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "Test"],
        capture_output=True, check=True,
    )
    readme = tmp_path / "README.md"
    readme.write_text("# Test\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True, check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-m", "init"],
        capture_output=True, check=True,
    )
    return tmp_path


# ═══════════════════════════════════════════════════════════════
# Import-availability guards
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def requires_ollama():
    """Skip if codomyrmex.llm.ollama is not importable."""
    pytest.importorskip("codomyrmex.llm.ollama")


@pytest.fixture
def requires_docker():
    """Skip if docker CLI is not available."""
    import subprocess
    try:
        subprocess.run(["docker", "--version"], capture_output=True, timeout=5, check=True)
    except Exception:
        pytest.skip("Docker not available")
