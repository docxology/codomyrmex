"""Real manuscript generation with isolated output and declared provenance."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="session")
def generated_manuscript_snapshot(tmp_path_factory) -> Path:
    """Generate from current inputs in a standalone temporary project.

    The production CLI retains its pinned-checkout validation. This unit-test
    project deliberately has no adjacent template and exercises the documented
    strict successor, without consulting an operator's sibling checkout.
    """
    source = Path(__file__).resolve().parents[3]
    project = tmp_path_factory.mktemp("manuscript-project")
    # Select public index inputs, excluding personal/untracked configuration and
    # Git submodule directories. Nested checks receive real independent copies.
    tracked = subprocess.run(
        ["git", "ls-files", "--stage", "-z"],
        cwd=source,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split("\0")
    surfaces = {"src", "docs", "config", "scripts", "tests", ".github"}
    for entry in tracked:
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        if metadata.split()[0] == "160000":
            continue
        relative = Path(name)
        if len(relative.parts) > 1 and relative.parts[0] not in surfaces:
            continue
        original = source / relative
        if not original.is_file():
            continue
        destination = project / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, destination, follow_symlinks=False)
    env = os.environ.copy()
    env.pop("TEMPLATE_REPO_ROOT", None)
    env["PYTHONPATH"] = str(project / "src") + os.pathsep + str(project)
    # Nested repository checks invoke uv. Reuse this already provisioned test
    # interpreter without creating an environment or syncing dependencies.
    env["UV_PROJECT_ENVIRONMENT"] = sys.prefix
    env["UV_NO_SYNC"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            str(project / "scripts/z_generate_manuscript_variables.py"),
            "--project-root",
            str(project),
        ],
        cwd=project,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode:
        pytest.fail(
            "Isolated manuscript generation failed:\n" + result.stdout + result.stderr,
            pytrace=False,
        )
    snapshot = project / "output/data/manuscript_variables.json"
    variables = json.loads(snapshot.read_text(encoding="utf-8"))
    config = yaml.safe_load((source / "docs/manuscript/config.yaml").read_text())
    assert (
        variables["REPRO_TEMPLATE_HYDRATION_MODE"] == "project-local-strict-successor"
    )
    assert (
        variables["REPRO_TEMPLATE_REVISION"].replace(" ", "")
        == config["template"]["revision"]
    )
    assert variables["REPRO_GIT_COMMIT"] == "unknown"
    assert (project / "output/manuscript/preamble.md").is_file()
    return snapshot
