#!/usr/bin/env python3
"""Analyze git diff for review hints (secrets, SQL concat, debug, TODOs, etc.)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Finding:
    category: str
    severity: str
    line_hint: str
    path: str


PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    (
        "hardcoded_secret",
        "high",
        re.compile(r"(?i)(api[_-]?key|password|secret|token)\s*=\s*['\"][^'\"]{8,}"),
    ),
    (
        "sql_concat",
        "high",
        re.compile(r"(?i)(execute|cursor\.execute)\s*\(\s*[\"'].*%s"),
    ),
    ("debugger", "medium", re.compile(r"\bdebugger\b|pdb\.set_trace|breakpoint\s*\(")),
    ("console_log", "low", re.compile(r"\bconsole\.(log|debug|info)\s*\(")),
    ("eslint_disable", "low", re.compile(r"eslint-disable(-next-line)?")),
    ("ts_any", "low", re.compile(r":\s*any\b")),
    ("todo_fixme", "note", re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")),
]


def git_diff(repo: Path, base: str, head: str) -> str:
    cmd = ["git", "-C", str(repo), "diff", f"{base}...{head}"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        msg = (
            proc.stderr.strip()
            or proc.stdout.strip()
            or f"git diff failed ({proc.returncode})"
        )
        raise RuntimeError(msg)
    return proc.stdout


def parse_diff_files(diff_text: str) -> dict[str, list[str]]:
    """Map path -> list of added/changed line contents (no leading +)."""
    files: dict[str, list[str]] = {}
    current: str | None = None
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            current = None
            continue
        if line.startswith("+++ b/"):
            current = line[6:].strip()
            if current == "/dev/null":
                current = None
            elif current:
                files.setdefault(current, [])
            continue
        if current and line.startswith("+") and not line.startswith("+++"):
            files[current].append(line[1:])
    return files


def analyze_diff(diff_text: str) -> list[Finding]:
    findings: list[Finding] = []
    files = parse_diff_files(diff_text)
    for path, lines in files.items():
        for i, content in enumerate(lines, start=1):
            for cat, sev, rx in PATTERNS:
                if rx.search(content):
                    findings.append(
                        Finding(
                            category=cat,
                            severity=sev,
                            line_hint=content[:200],
                            path=f"{path}:{i}",
                        )
                    )
    return findings


def score(findings: list[Finding]) -> tuple[int, str]:
    weights = {"high": 4, "medium": 2, "low": 1, "note": 0}
    raw = sum(weights.get(f.severity, 1) for f in findings)
    complexity = min(10, max(1, raw // 3 + 1))
    critical = sum(1 for f in findings if f.severity == "high")
    if critical >= 3 or raw > 40:
        risk = "critical"
    elif critical >= 1 or raw > 20:
        risk = "high"
    elif raw > 8:
        risk = "medium"
    else:
        risk = "low"
    return complexity, risk


def main() -> int:
    parser = argparse.ArgumentParser(description="PR / branch diff analyzer")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--base", default="main", help="Base ref (default: main)")
    parser.add_argument("--head", default="HEAD", help="Head ref (default: HEAD)")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()
    repo = args.repo.resolve()
    try:
        diff = git_diff(repo, args.base, args.head)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    findings = analyze_diff(diff)
    complexity, risk = score(findings)
    payload = {
        "base": args.base,
        "head": args.head,
        "complexity_score": complexity,
        "risk": risk,
        "findings_count": len(findings),
        "findings": [asdict(f) for f in findings],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    print(f"Diff analysis: {args.base}...{args.head}")
    print(f"  Complexity (1-10): {complexity}")
    print(f"  Risk band: {risk}")
    print(f"  Findings: {len(findings)}")
    for f in findings[:50]:
        print(f"  [{f.severity}] {f.category} @ {f.path}")
    if len(findings) > 50:
        print(f"  ... and {len(findings) - 50} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
