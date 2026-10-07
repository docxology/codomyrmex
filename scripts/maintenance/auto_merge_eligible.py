#!/usr/bin/env python3
"""Decide which open pull requests the Auto-Merge workflow may merge.

A pull request is eligible only when a person has applied the ``auto-merge``
label, every check has finished, and none of them failed. Skipped and
neutral checks do not block (path-filtered jobs report SKIPPED).

Previously the workflow also merged any PR whose *branch name* contained
fragments such as ``fix/``, ``add-`` or ``feat-``, and ``pr-labeler.yml``
applied ``auto-merge`` to every agent and Dependabot PR automatically, so
unreviewed agent changes were merged as soon as CI passed. The label is now
the only signal, and it is never applied by automation.

Usage (as in .github/workflows/auto-merge.yml)::

    gh pr list --state open --json number,labels,statusCheckRollup,mergeable,isDraft \\
        | python scripts/maintenance/auto_merge_eligible.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

LABEL = "auto-merge"
PASSING = frozenset({"SUCCESS", "SKIPPED", "NEUTRAL"})


def check_outcome(check: dict[str, Any]) -> str:
    """Normalise a statusCheckRollup entry to an upper-case outcome.

    CheckRun entries carry ``status``/``conclusion``; legacy StatusContext
    entries carry ``state``. Anything unfinished is ``PENDING``.
    """
    if "state" in check and "conclusion" not in check:
        state = str(check.get("state") or "").upper()
        return {"SUCCESS": "SUCCESS", "ERROR": "FAILURE"}.get(state, state)
    if str(check.get("status") or "").upper() != "COMPLETED":
        return "PENDING"
    return str(check.get("conclusion") or "").upper() or "PENDING"


def eligibility(pr: dict[str, Any]) -> tuple[bool, str]:
    """Return (eligible, reason) for one ``gh pr list --json`` entry."""
    labels = {label.get("name") for label in pr.get("labels") or []}
    if LABEL not in labels:
        return False, f"no '{LABEL}' label"
    if pr.get("isDraft"):
        return False, "draft"
    if pr.get("mergeable") != "MERGEABLE":
        return False, f"mergeable={pr.get('mergeable')}"
    checks = pr.get("statusCheckRollup") or []
    if not checks:
        return False, "no checks reported"
    blocking = sorted(
        {
            f"{check.get('name') or check.get('context')}={outcome}"
            for check in checks
            if (outcome := check_outcome(check)) not in PASSING
        }
    )
    if blocking:
        return False, "blocked by " + ", ".join(blocking[:5])
    return True, "all checks passed"


def main() -> int:
    prs = json.load(sys.stdin)
    for pr in prs:
        ok, reason = eligibility(pr)
        print(
            f"#{pr['number']}: {'merge' if ok else 'skip'} ({reason})", file=sys.stderr
        )
        if ok:
            print(pr["number"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
