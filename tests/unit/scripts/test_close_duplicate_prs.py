"""Regression tests for the duplicate-PR sentinel's pure grouping logic.

The scheduled ``Duplicate PR Sentinel`` workflow crashed every run with
``KeyError: 'rep_title'`` (the comment template referenced a field that was
never supplied) and, had it run, would have chosen the PR with the *fewest*
changed files as each family's representative because the sort key was
negated *and* reversed.
"""

from __future__ import annotations

import importlib.util
from datetime import datetime, timezone

import pytest
from tests.support.repo_paths import REPO_ROOT


@pytest.fixture(scope="module")
def sentinel():
    script = REPO_ROOT / "scripts" / "maintenance" / "close_duplicate_prs.py"
    spec = importlib.util.spec_from_file_location("close_duplicate_prs", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pr(number: int, title: str, files: list[str], created: str) -> dict:
    return {
        "number": number,
        "title": title,
        "createdAt": created,
        "_files": [{"path": p} for p in files],
    }


@pytest.mark.unit
def test_close_comment_renders_representative_title(sentinel) -> None:
    text = sentinel.close_comment(42, "Palette: add ARIA labels")
    assert "#42 (Palette: add ARIA labels)" in text
    assert "<!-- close_duplicate_prs.py -->" in text


@pytest.mark.unit
def test_title_signature_ignores_emoji_and_stopwords(sentinel) -> None:
    a, sig_a = sentinel.title_signature(
        "🎨 Palette: Add ARIA labels to icon-only buttons"
    )
    b, sig_b = sentinel.title_signature(
        "Palette - add aria LABELS to icon only buttons"
    )
    assert a == b
    assert sig_a == sig_b
    assert "add" not in a


@pytest.mark.unit
def test_representative_has_most_substantive_files(sentinel) -> None:
    journal_only = _pr(
        1, "Palette: ARIA labels", [".jules/palette.md"], "2026-09-20T00:00:00Z"
    )
    real = _pr(
        2,
        "Palette: ARIA labels",
        [".jules/palette.md", "src/app.js", "src/chat.js"],
        "2026-09-10T00:00:00Z",
    )
    newer_small = _pr(3, "Palette: ARIA labels", ["src/app.js"], "2026-09-25T00:00:00Z")
    families = sentinel.build_families([journal_only, real, newer_small], 0.6)
    assert len(families) == 1
    assert [p["number"] for p in families[0]] == [2, 3, 1]


@pytest.mark.unit
def test_newest_wins_ties(sentinel) -> None:
    old = _pr(10, "Bolt: hoist regex", ["src/a.py"], "2026-09-01T00:00:00Z")
    new = _pr(11, "Bolt: hoist regex", ["src/a.py"], "2026-09-05T00:00:00Z")
    family = [old, new]
    sentinel.order_family(family)
    assert family[0]["number"] == 11


@pytest.mark.unit
def test_disjoint_files_do_not_form_a_family(sentinel) -> None:
    a = _pr(20, "Bolt: hoist regex", ["src/a.py"], "2026-09-01T00:00:00Z")
    b = _pr(21, "Bolt: hoist regex", ["src/b.py"], "2026-09-02T00:00:00Z")
    assert sentinel.build_families([a, b], 0.6) == []


@pytest.mark.unit
def test_singletons_are_not_families(sentinel) -> None:
    only = _pr(30, "Sentinel: fix XSS", ["src/app.js"], "2026-09-01T00:00:00Z")
    assert sentinel.build_families([only], 0.6) == []


def _gql_pr(number: int, created: str, paths: list[str]) -> dict:
    return {
        "number": number,
        "title": "Bolt: hoist regex",
        "createdAt": created,
        "files": {"nodes": [{"path": p} for p in paths]},
    }


@pytest.mark.unit
def test_plan_closures_respects_age_and_limit(sentinel) -> None:
    now = datetime(2026, 10, 6, tzinfo=timezone.utc)  # noqa: UP017
    prs = [
        _gql_pr(1, "2026-09-01T00:00:00Z", ["src/a.py"]),
        _gql_pr(2, "2026-09-02T00:00:00Z", ["src/a.py"]),
        _gql_pr(3, "2026-10-05T00:00:00Z", ["src/a.py"]),
        _gql_pr(4, "2026-09-03T00:00:00Z", ["src/a.py", "src/b.py"]),
    ]
    families, candidates, titles = sentinel.plan_closures(
        prs, now=now, min_similarity=0.6, older_than=7
    )
    assert len(families) == 1
    # #4 has the most files -> representative; #3 is too fresh to close.
    assert sorted(candidates) == [(1, 4), (2, 4)]
    assert titles == {4: "Bolt: hoist regex"}

    _, limited, _ = sentinel.plan_closures(
        [dict(p) for p in prs], now=now, min_similarity=0.6, limit=1
    )
    assert len(limited) == 1
