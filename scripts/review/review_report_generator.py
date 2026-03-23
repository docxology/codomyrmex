#!/usr/bin/env python3
"""Merge PR analysis, quality JSON, and SARIF summaries into one report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from sarif_utils import merge_sarif_files, summarize_sarif


def verdict(
    pr: dict[str, Any] | None,
    quality: dict[str, Any] | None,
    sarif_summary: dict[str, Any] | None,
) -> tuple[str, int]:
    """Return (verdict, score 0-100) using heuristic rules from code-reviewer skill."""
    score = 100
    high = 0
    critical = 0
    if pr:
        risk = pr.get("risk", "low")
        if risk == "critical":
            critical += 1
            score -= 40
        elif risk == "high":
            high += 2
            score -= 25
        elif risk == "medium":
            high += 1
            score -= 10
        score -= min(20, pr.get("findings_count", 0))
    if quality:
        for issue in quality.get("issues") or []:
            if issue.get("severity") == "high":
                high += 1
                score -= 8
            elif issue.get("severity") == "medium":
                score -= 3
            else:
                score -= 1
    if sarif_summary:
        errs = (sarif_summary.get("by_level") or {}).get("error", 0)
        score -= min(30, errs * 2)
        if errs > 5:
            high += 2
    score = max(0, min(100, score))
    if critical or score < 50:
        return "block", score
    if score < 75 or high > 2:
        return "request_changes", score
    if score >= 90 and high == 0:
        return "approve", score
    return "approve_with_suggestions", score


def markdown_report(
    pr: dict[str, Any] | None,
    quality: dict[str, Any] | None,
    sarif_summary: dict[str, Any] | None,
    v: str,
    sc: int,
    repo: str = "",
) -> str:
    lines = [
        "# Review report",
        "",
    ]
    if repo:
        lines.append(f"**Repository**: `{repo}`")
        lines.append("")
    lines += [
        f"**Verdict**: `{v}`  ",
        f"**Score**: {sc}/100",
        "",
    ]
    if pr:
        lines += [
            "## PR diff analysis",
            f"- Complexity: {pr.get('complexity_score')}/10",
            f"- Risk: {pr.get('risk')}",
            f"- Findings: {pr.get('findings_count')}",
            "",
        ]
    if quality:
        lines += [
            "## Structural quality",
            f"- Issues: {quality.get('issues_count')}",
            "",
        ]
    if sarif_summary:
        lines += [
            "## SARIF summary",
            f"- Total results: {sarif_summary.get('total_results')}",
            f"- By level: `{sarif_summary.get('by_level')}`",
            "",
        ]
    lines.append("## Action items")
    lines.append("1. Triage findings above against team policy.")
    lines.append("2. Re-run security workflow for fresh SARIF if needed.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Combined review report")
    parser.add_argument("repo", type=Path, help="Repository root (informational)")
    parser.add_argument("--pr-analysis", type=Path, help="JSON from pr_analyzer.py")
    parser.add_argument(
        "--quality-analysis", type=Path, help="JSON from code_quality_checker.py"
    )
    parser.add_argument(
        "--sarif", type=Path, nargs="*", default=[], help="SARIF files to summarize"
    )
    parser.add_argument("--format", choices=["markdown", "text"], default="text")
    parser.add_argument("--output", type=Path, help="Write report to file")
    args = parser.parse_args()
    _repo = args.repo.resolve()

    pr_data: dict[str, Any] | None = None
    if args.pr_analysis:
        pr_data = json.loads(args.pr_analysis.read_text(encoding="utf-8"))
    qual_data: dict[str, Any] | None = None
    if args.quality_analysis:
        qual_data = json.loads(args.quality_analysis.read_text(encoding="utf-8"))

    sarif_combined: dict[str, Any] | None = None
    if args.sarif:
        merged = merge_sarif_files([p.resolve() for p in args.sarif])
        sarif_combined = summarize_sarif(merged)

    v, sc = verdict(pr_data, qual_data, sarif_combined)
    if args.format == "markdown":
        body = markdown_report(
            pr_data, qual_data, sarif_combined, v, sc, repo=str(_repo)
        )
    else:
        body = (
            f"Verdict: {v}\nScore: {sc}/100\n"
            f"PR: {pr_data is not None} Quality: {qual_data is not None} SARIF files: {len(args.sarif)}"
        )
        if sarif_combined:
            body += f"\nSARIF results: {sarif_combined.get('total_results')}"

    if args.output:
        args.output.write_text(body, encoding="utf-8")
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
