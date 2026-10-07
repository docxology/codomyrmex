"""A small, fully known git history for the GitPython-backed analysis tests.

The tests used to analyse the codomyrmex checkout itself, so every
contributor/churn/hotspot call walked thousands of commits (~18 s each in
CI), results depended on clone depth, and assertions could only check
shapes. This repository is built once per session with fixed authors,
dates and files, so the tests are fast and can assert exact values.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import git
import pytest

ADA = git.Actor("Ada Lovelace", "ada@example.invalid")
GRACE = git.Actor("Grace Hopper", "grace@example.invalid")

# (author, ISO date, message, {path: content}) in commit order.
HISTORY: tuple[tuple[git.Actor, str, str, dict[str, str]], ...] = (
    (
        ADA,
        "2026-01-05T09:00:00+00:00",
        "Initial layout",
        {
            "README.md": "# Sample\n",
            "src/core/engine.py": "def run():\n    return 1\n",
            "src/cli/main.py": "print('cli')\n",
        },
    ),
    (
        ADA,
        "2026-01-06T09:00:00+00:00",
        "Engine: add step",
        {
            "src/core/engine.py": "def run():\n    return step()\n\n\ndef step():\n    return 1\n"
        },
    ),
    (
        GRACE,
        "2026-01-20T09:00:00+00:00",
        "Add engine tests",
        {"tests/test_engine.py": "def test_run():\n    assert True\n"},
    ),
    (
        ADA,
        "2026-02-02T09:00:00+00:00",
        "Engine: handle errors",
        {
            "src/core/engine.py": (
                "def run():\n    try:\n        return step()\n"
                "    except ValueError:\n        return 0\n\n\n"
                "def step():\n    return 1\n"
            )
        },
    ),
    (
        GRACE,
        "2026-02-03T09:00:00+00:00",
        "Add util helpers",
        {"src/core/util.py": "def clamp(x):\n    return max(0, x)\n"},
    ),
    (
        ADA,
        "2026-03-10T09:00:00+00:00",
        "Document usage",
        {"README.md": "# Sample\n\nRun `sample`.\n", "docs/guide.md": "Guide\n"},
    ),
    (
        GRACE,
        "2026-03-11T09:00:00+00:00",
        "Engine: use clamp",
        {
            "src/core/engine.py": (
                "from util import clamp\n\n\ndef run():\n    try:\n"
                "        return clamp(step())\n    except ValueError:\n"
                "        return 0\n\n\ndef step():\n    return 1\n"
            )
        },
    ),
    (
        ADA,
        "2026-03-12T09:00:00+00:00",
        "README: badges",
        {"README.md": "# Sample\n\n![ok]\n\nRun `sample`.\n"},
    ),
)


@dataclass(frozen=True)
class HistoryRepo:
    path: str
    head_sha: str


@pytest.fixture(scope="session")
def history_repo(tmp_path_factory: pytest.TempPathFactory) -> HistoryRepo:
    root: Path = tmp_path_factory.mktemp("history_repo")
    repo = git.Repo.init(root, initial_branch="trunk")
    with repo.config_writer() as config:
        config.set_value("user", "name", "Fixture")
        config.set_value("user", "email", "fixture@example.invalid")
    for author, date, message, files in HISTORY:
        for relative, content in files.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        repo.index.add(list(files))
        # git's raw "<epoch> <offset>" form; GitPython rejects ISO offsets.
        stamp = f"{int(datetime.fromisoformat(date).timestamp())} +0000"
        repo.index.commit(
            message,
            author=author,
            committer=author,
            author_date=stamp,
            commit_date=stamp,
        )
    repo.create_head("feature/cli", repo.head.commit.parents[0])
    head_sha = repo.head.commit.hexsha
    repo.close()
    return HistoryRepo(path=str(root), head_sha=head_sha)
