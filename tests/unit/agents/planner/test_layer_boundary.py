"""Layer-boundary guardrails for planner feedback modules."""

from pathlib import Path

import pytest
from tests.support.repo_paths import PACKAGE_ROOT, REPO_ROOT

pytestmark = pytest.mark.unit


def _repo_root() -> Path:
    return REPO_ROOT


def test_planner_feedback_modules_do_not_import_orchestrator() -> None:
    root = _repo_root()
    for rel in (
        "src/codomyrmex/agents/planner/feedback_loop.py",
        "src/codomyrmex/agents/planner/plan_evaluator.py",
    ):
        text = (root / rel).read_text(encoding="utf-8")
        assert "codomyrmex.orchestrator" not in text
