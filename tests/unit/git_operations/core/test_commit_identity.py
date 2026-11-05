"""A caller-supplied commit identity must reach the author and the committer.

``--author`` alone leaves the committer to configuration, so a caller that passes an
identity and inherits no configured user gets a commit made by whatever ambient
identity the process happens to carry. These tests pin the per-command behaviour and
pin the refusal, so the suite never needs a session-wide identity to commit.
"""

import os
import subprocess
from pathlib import Path

import pytest
from tests.support.git_temp_repository import initialize_repository

from codomyrmex.git_operations import commit_changes

pytestmark = pytest.mark.unit

_IDENTITY_VARIABLES = (
    "GIT_AUTHOR_NAME",
    "GIT_AUTHOR_EMAIL",
    "GIT_COMMITTER_NAME",
    "GIT_COMMITTER_EMAIL",
)


@pytest.fixture
def unconfigured_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A repository with no identity anywhere, as in a bare CI runner."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for variable in _IDENTITY_VARIABLES:
        monkeypatch.delenv(variable, raising=False)

    repo = tmp_path / "repo"
    assert initialize_repository(repo, initial_commit=False, root=tmp_path)
    # initialize_repository writes the usual test identity; clear it for this test.
    subprocess.run(
        ["git", "config", "--unset-all", "user.name"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    subprocess.run(
        ["git", "config", "--unset-all", "user.email"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    (repo / "note.txt").write_text("note\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "note.txt"], cwd=repo, check=True, capture_output=True
    )
    return repo


def _commit_identities(repo: Path) -> str:
    """Return ``author|committer`` for the most recent commit."""
    return subprocess.run(
        ["git", "log", "-1", "--format=%an <%ae>|%cn <%ce>"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def test_commit_identity_flags_cover_author_and_committer(
    unconfigured_repo: Path,
) -> None:
    """Passing a name and email settles both identities without any configuration."""
    sha = commit_changes(
        "per-command identity",
        str(unconfigured_repo),
        author_name="Per Command",
        author_email="per@command.invalid",
        stage_all=False,
    )

    assert sha is not None
    assert _commit_identities(unconfigured_repo) == (
        "Per Command <per@command.invalid>|Per Command <per@command.invalid>"
    )


def test_commit_uses_the_repository_local_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With no global configuration, the repository's own config is enough to commit."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for variable in _IDENTITY_VARIABLES:
        monkeypatch.delenv(variable, raising=False)

    repo = tmp_path / "repo"
    assert initialize_repository(repo, initial_commit=False, root=tmp_path)
    (repo / "note.txt").write_text("note\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "note.txt"], cwd=repo, check=True, capture_output=True
    )

    sha = commit_changes("local identity", str(repo), stage_all=False)

    assert sha is not None
    assert _commit_identities(repo) == (
        "Codomyrmex Tests <tests@codomyrmex.dev>|"
        "Codomyrmex Tests <tests@codomyrmex.dev>"
    )
