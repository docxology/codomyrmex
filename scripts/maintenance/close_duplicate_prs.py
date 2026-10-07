#!/usr/bin/env python3
"""scripts/maintenance/close_duplicate_prs.py

Detects duplicate-family pull requests and closes the stale members,
keeping one representative per family.

Motivation (2026-09 triage): agent-generated PR floods produced dozens of
near-identical open PRs (same persona, same target files, same change) while
one representative per family was already merged. This script groups open
PRs into families and closes non-representative members with an explanatory
comment. It never closes the representative.

Usage:
    uv run --locked python scripts/maintenance/close_duplicate_prs.py [--help]
    uv run --locked python scripts/maintenance/close_duplicate_prs.py             # dry-run (default)
    uv run --locked python scripts/maintenance/close_duplicate_prs.py --apply     # close + comment
    uv run --locked python scripts/maintenance/close_duplicate_prs.py --older-than 7

    --dry-run          Print the plan without mutating anything (default).
    --apply            Actually close duplicate PRs with comments.
    --older-than DAYS  Only PRs older than DAYS are close candidates
                       (protects fresh PRs from an overeager sweep).
    --min-similarity F Title similarity threshold for family grouping
                       (default 0.6).

Requires an authenticated ``gh`` CLI (honours ``GH_TOKEN``).
Output is deterministic and repository-relative; no credentials are printed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone

GH = "gh"
GRAPHQL_LIMIT = 60
FILE_LIMIT = 50
DEFAULT_REPO = "docxology/codomyrmex"

CLOSE_COMMENT_TEMPLATE = (
    "Closing as a duplicate of #{rep} ({rep_title}).\n\n"
    "Automated triage grouped this PR into the same duplicate family: same "
    "persona/intent, overlapping target files, and an equivalent change. "
    "#{rep} remains open as the family representative.\n\n"
    "If this PR contains something #{rep} does not, please comment with the "
    "specific delta (file + line) and it can be reopened.\n\n"
    "<!-- close_duplicate_prs.py -->"
)


def gh_graphql(query: str, variables: dict | None = None) -> dict:
    """Run one GraphQL query via gh and return the parsed data payload."""
    cmd = [GH, "api", "graphql", "-f", f"query={query}"]
    for key, value in (variables or {}).items():
        if value is None:
            continue
        cmd += ["-F", f"{key}={value}"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["data"]


def list_open_prs(repo: str = DEFAULT_REPO) -> list[dict]:
    """Return all open PRs with title/author/dates and up to FILE_LIMIT files."""
    owner, name = repo.split("/", 1)
    query = f"""
    query($cursor: String, $owner: String!, $name: String!) {{
      repository(owner: $owner, name: $name) {{
        pullRequests(first: {GRAPHQL_LIMIT}, after: $cursor, states: OPEN, orderBy: {{field: CREATED_AT, direction: ASC}}) {{
          pageInfo {{ hasNextPage endCursor }}
          nodes {{
            number title createdAt updatedAt
            author {{ login }}
            headRefName
            files(first: {FILE_LIMIT}) {{ nodes {{ path }} }}
          }}
        }}
      }}
    }}
    """
    prs: list[dict] = []
    cursor = None
    while True:
        data = gh_graphql(query, {"cursor": cursor, "owner": owner, "name": name})[
            "repository"
        ]["pullRequests"]
        prs.extend(data["nodes"])
        if not data["pageInfo"]["hasNextPage"]:
            break
        cursor = data["pageInfo"]["endCursor"]
    return prs


STRIP_TOKENS = re.compile(r"[^\w\s]")


def title_signature(title: str) -> tuple[frozenset[str], str]:
    """Return (token set, normalized string) used for family grouping."""
    text = STRIP_TOKENS.sub(" ", title).lower()
    words = [w for w in text.split() if len(w) > 2]
    # Drop generic words that appear in every flood title.
    stop = {
        "feat",
        "fix",
        "perf",
        "test",
        "chore",
        "refactor",
        "the",
        "and",
        "for",
        "with",
        "add",
        "improve",
        "improvement",
    }
    tokens = frozenset(w for w in words if w not in stop)
    return tokens, " ".join(sorted(tokens))


def similarity(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def file_overlap(paths_a: set[str], paths_b: set[str]) -> float:
    if not paths_a or not paths_b:
        return 0.0
    return len(paths_a & paths_b) / min(len(paths_a), len(paths_b))


JOURNAL_PREFIXES = (".jules/",)


def substantive_paths(pr: dict) -> set[str]:
    """Changed paths excluding agent journal notes (``.jules/``)."""
    return {
        f["path"]
        for f in pr.get("_files", [])
        if not f["path"].startswith(JOURNAL_PREFIXES)
    }


def substantive_file_count(pr: dict) -> int:
    """Count changed files that are not agent journal notes."""
    return len(substantive_paths(pr))


def order_family(cluster: list[dict]) -> None:
    """Sort a family in place so its representative comes first.

    Representative = member with the most substantive (non-journal) file
    changes; the newest PR wins ties. Journal-only PRs therefore never
    represent a family while a member with real changes exists.
    """
    cluster.sort(
        key=lambda p: (substantive_file_count(p), p["createdAt"]),
        reverse=True,
    )


def build_families(prs: list[dict], min_similarity: float) -> list[list[dict]]:
    """Greedy agglomeration: same token signature or high similarity + file overlap."""
    by_sig: dict[str, list[dict]] = defaultdict(list)
    for pr in prs:
        tokens, sig = title_signature(pr["title"])
        pr["_tokens"] = tokens
        by_sig[sig].append(pr)
    families: list[list[dict]] = []
    for sig, members in by_sig.items():
        if len(members) == 1:
            continue
        # Refine: only same-family when substantive file paths overlap with
        # the cluster so far (journal-only members join on title alone).
        clusters: list[list[dict]] = []
        for pr in members:
            paths = substantive_paths(pr)
            placed = False
            for cluster in clusters:
                cluster_paths = set().union(*(substantive_paths(m) for m in cluster))
                if similarity(
                    pr["_tokens"], cluster[0]["_tokens"]
                ) >= min_similarity and (
                    not paths
                    or not cluster_paths
                    or file_overlap(paths, cluster_paths) >= 0.5
                ):
                    cluster.append(pr)
                    placed = True
                    break
            if not placed:
                clusters.append([pr])
        clusters = [c for c in clusters if len(c) > 1]
        if clusters:
            for cluster in clusters:
                order_family(cluster)
            families.extend(clusters)
    return families


def close_comment(rep_number: int, rep_title: str) -> str:
    return CLOSE_COMMENT_TEMPLATE.format(rep=rep_number, rep_title=rep_title)


def plan_closures(
    prs: list[dict],
    *,
    now: datetime,
    min_similarity: float,
    older_than: int = 0,
    limit: int = 0,
) -> tuple[list[list[dict]], list[tuple[int, int]], dict[int, str]]:
    """Group PRs and return ``(families, candidates, representative titles)``.

    ``candidates`` holds ``(pr_number, representative_number)`` pairs. PRs
    younger than ``older_than`` days are never candidates; ``limit`` caps the
    number of closures (0 = no cap). Pure: performs no I/O.
    """
    for pr in prs:
        pr["_files"] = (
            pr.pop("files")["nodes"] if "files" in pr else pr.get("_files", [])
        )
        created = datetime.fromisoformat(pr["createdAt"])
        pr["_age_days"] = (now - created).days

    families = build_families(prs, min_similarity)
    candidates: list[tuple[int, int]] = []
    rep_titles: dict[int, str] = {}
    for family in families:
        rep = family[0]
        rep_titles[rep["number"]] = rep["title"]
        for member in family[1:]:
            if older_than > 0 and member["_age_days"] < older_than:
                continue
            candidates.append((member["number"], rep["number"]))
    if limit:
        candidates = candidates[:limit]
    return families, candidates, rep_titles


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument(
        "--apply", action="store_true", help="close + comment (default: dry-run)"
    )
    parser.add_argument(
        "--older-than",
        type=int,
        default=0,
        metavar="DAYS",
        help="only close PRs older than this many days",
    )
    parser.add_argument("--min-similarity", type=float, default=0.6)
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO),
        help="owner/name (default: $GITHUB_REPOSITORY or docxology/codomyrmex)",
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="cap number of closes (0 = no cap)"
    )
    args = parser.parse_args(argv)

    prs = list_open_prs(args.repo)
    plan = plan_closures(
        prs,
        now=datetime.now(tz=timezone.utc),  # noqa: UP017 (datetime.UTC absent in this runtime)
        min_similarity=args.min_similarity,
        older_than=args.older_than,
        limit=args.limit,
    )
    families, candidates, rep_titles = plan

    print(
        f"open PRs: {len(prs)} | duplicate families: {len(families)} | close candidates: {len(candidates)}"
    )
    for pr_number, rep_number in sorted(candidates):
        print(f"  #{pr_number} -> duplicate of #{rep_number}")

    if not args.apply:
        print("dry-run: no PRs were closed. Re-run with --apply to execute.")
        return 0

    failed = 0
    for pr_number, rep_number in candidates:
        comment = close_comment(rep_number, rep_titles[rep_number])
        result = subprocess.run(
            [
                GH,
                "pr",
                "close",
                str(pr_number),
                "--repo",
                args.repo,
                "--comment",
                comment,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failed += 1
            print(f"FAILED #{pr_number}: {result.stderr.strip()}", file=sys.stderr)
    print(f"applied: closed {len(candidates) - failed}/{len(candidates)} duplicate PRs")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
