"""Exercise the actual Git index, including staged path changes."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[3] / "scripts/audits/audit_path_portability.py"
)


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("paths", "expected"),
    [
        (["docs/README.md", "docs/readme.md"], 1),
        (["Modules/a.py", "modules/b.py"], 1),
        (["caf\u00e9/a.py", "cafe\u0301/b.py"], 1),
        (["one/README.md", "two/README.md"], 0),
        (["a space/a.py", "a space/b.py"], 0),
    ],
)
def test_real_git_index_portability(tmp_path, paths, expected):
    git(tmp_path, "init")
    git(tmp_path, "config", "core.precomposeunicode", "false")
    blob = (
        subprocess.run(
            ["git", "-C", str(tmp_path), "hash-object", "-w", "--stdin"],
            input=b"content\n",
            capture_output=True,
            check=True,
        )
        .stdout.decode()
        .strip()
    )
    # Index-only paths represent collisions faithfully even on macOS.
    for path in paths:
        git(tmp_path, "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == expected, result.stdout + result.stderr
    assert f"{expected} collisions" in result.stdout
    git(tmp_path, "update-index", "--force-remove", "--", paths[-1])
    after = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert after.returncode == 0, after.stdout + after.stderr


@pytest.mark.unit
def test_missing_git_index_fails(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2


@pytest.mark.unit
def test_nested_directory_cannot_claim_repository_audit(tmp_path):
    git(tmp_path, "init")
    nested = tmp_path / "nested"
    nested.mkdir()
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(nested)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "Git repository root" in result.stderr
