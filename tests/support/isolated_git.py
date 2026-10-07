"""Run code that creates git worktrees against a throwaway repository.

The Hermes worktree tools run ``git worktree add -b hermes/<id>`` in the
current directory and place the checkout under ``~/.codomyrmex/worktrees``.
Tests that called them from the project root left a real worktree and branch
in the developer's clone (``hermes/test-wt-001``) on every run. This helper
points both the working directory and the home directory at ``tmp_path``.
Only environment variables and ``chdir`` are patched, as the zero-mock policy
allows.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def isolated_git_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a one-commit repository, chdir into it and isolate ``~``."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))  # expanduser on Windows

    repo = tmp_path / "repo"
    repo.mkdir()
    git = ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid"]
    subprocess.run([*git, "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        [*git, "commit", "-q", "--allow-empty", "-m", "init"], cwd=repo, check=True
    )
    monkeypatch.chdir(repo)
    return repo


def branches(repo: Path) -> set[str]:
    """Local branch names of ``repo``."""
    out = subprocess.run(
        ["git", "branch", "--format=%(refname:short)"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return set(out.split())
