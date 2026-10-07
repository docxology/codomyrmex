"""Eligibility rules for the Auto-Merge workflow.

Regression: the workflow merged any passing PR whose branch name contained
``fix/``, ``add-``, ``feat-`` and similar fragments, and the labeler put
``auto-merge`` on every agent and Dependabot PR, so unreviewed agent changes
would merge as soon as CI was green.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys

import pytest
import yaml
from tests.support.repo_paths import REPO_ROOT

SCRIPT = REPO_ROOT / "scripts" / "maintenance" / "auto_merge_eligible.py"


@pytest.fixture(scope="module")
def rules():
    spec = importlib.util.spec_from_file_location("auto_merge_eligible", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _check(name: str, conclusion: str | None, status: str = "COMPLETED") -> dict:
    return {"__typename": "CheckRun", "name": name, "status": status,
            "conclusion": conclusion}  # fmt: skip


def _pr(number: int = 1, labels=("auto-merge",), checks=None, **extra) -> dict:
    return {
        "number": number,
        "labels": [{"name": label} for label in labels],
        "mergeable": "MERGEABLE",
        "isDraft": False,
        "statusCheckRollup": checks
        if checks is not None
        else [_check("ci", "SUCCESS"), _check("docs", "SKIPPED")],
        **extra,
    }


@pytest.mark.unit
def test_labelled_green_pr_is_eligible(rules) -> None:
    assert rules.eligibility(_pr()) == (True, "all checks passed")


@pytest.mark.unit
def test_label_is_required_whatever_the_branch(rules) -> None:
    ok, reason = rules.eligibility(_pr(labels=("jules", "agent-pr", "automated")))
    assert not ok
    assert "auto-merge" in reason


@pytest.mark.unit
@pytest.mark.parametrize(
    "check",
    [
        _check("ci", "FAILURE"),
        _check("ci", "CANCELLED"),
        _check("ci", "TIMED_OUT"),
        _check("ci", None, status="IN_PROGRESS"),
        {"__typename": "StatusContext", "context": "legacy", "state": "PENDING"},
        {"__typename": "StatusContext", "context": "legacy", "state": "ERROR"},
    ],
)
def test_unfinished_or_failed_checks_block(rules, check) -> None:
    ok, reason = rules.eligibility(_pr(checks=[_check("ok", "SUCCESS"), check]))
    assert not ok
    assert reason.startswith("blocked by")


@pytest.mark.unit
def test_drafts_conflicts_and_missing_checks_block(rules) -> None:
    assert not rules.eligibility(_pr(isDraft=True))[0]
    assert not rules.eligibility(_pr(mergeable="CONFLICTING"))[0]
    assert not rules.eligibility(_pr(checks=[]))[0]


@pytest.mark.unit
def test_cli_prints_only_eligible_numbers() -> None:
    prs = [_pr(7), _pr(8, labels=()), _pr(9, checks=[_check("ci", "FAILURE")])]
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(prs),
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.split() == ["7"]
    assert "#8: skip" in result.stderr


@pytest.mark.unit
def test_labeler_never_applies_auto_merge() -> None:
    labeler = (REPO_ROOT / ".github/workflows/pr-labeler.yml").read_text(
        encoding="utf-8"
    )
    workflow = yaml.safe_load(labeler)
    script = "\n".join(
        step.get("run", "")
        for job in workflow["jobs"].values()
        for step in job.get("steps", [])
    )
    assert '"auto-merge"' not in script
