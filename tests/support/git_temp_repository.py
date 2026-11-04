"""Create throwaway Git repositories whose identity lives inside the repository.

A session-wide identity (``GIT_CONFIG_GLOBAL`` pointing at a temporary config, or
``GIT_AUTHOR_*`` left in the environment) applies to every Git process the test
session starts, including one that outlives teardown and touches a repository the
test does not own. A temporary repository carries its identity in its own
``.git/config`` instead, so the identity is scoped to the repository that is
supposed to have it and nothing has to be patched for the whole process.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

TEST_IDENTITY_NAME = "Codomyrmex Tests"
TEST_IDENTITY_EMAIL = "tests@codomyrmex.dev"

_TIMEOUT = 60


def assert_contained(path: str | Path, root: str | Path) -> Path:
    """Return ``path`` resolved, refusing a target outside the test's own tree."""
    resolved = Path(path).resolve()
    boundary = Path(root).resolve()
    if resolved != boundary and not resolved.is_relative_to(boundary):
        raise AssertionError(
            f"{resolved} is outside the test's own tree {boundary}; "
            "a test must not operate on a repository it does not own"
        )
    return resolved


def initialize_repository(
    repository_path: str | Path,
    *,
    initial_commit: bool = True,
    root: str | Path | None = None,
    name: str = TEST_IDENTITY_NAME,
    email: str = TEST_IDENTITY_EMAIL,
) -> bool:
    """Initialise a temporary repository and give it a local commit identity.

    Args:
        repository_path: Directory to initialise. Created when absent.
        initial_commit: Create the README commit, as ``initialize_git_repository`` does.
        root: When given, the repository must live inside this directory.
        name: Local ``user.name`` for commits made in this repository.
        email: Local ``user.email`` for commits made in this repository.

    Returns:
        True when the repository was created, matching ``initialize_git_repository``.
    """
    from codomyrmex.git_operations import initialize_git_repository

    path = Path(repository_path)
    if root is not None:
        assert_contained(path, root)
    if not initialize_git_repository(str(path), initial_commit=initial_commit):
        return False
    for key, value in (("user.name", name), ("user.email", email)):
        subprocess.run(
            ["git", "config", key, value],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_TIMEOUT,
        )
    return True
