"""SARIF 2.1.0 helpers for merge and summary (stdlib only)."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import unquote


def normalize_uri(uri: str | None) -> str:
    """Normalize artifact URI for stable keys (strip file://, decode, POSIX)."""
    if not uri:
        return ""
    u = uri.strip().removeprefix("file://")
    u = unquote(u)
    return str(Path(u).as_posix())


def result_fingerprint(result: dict[str, Any]) -> tuple[Any, ...]:
    """Stable dedupe key: fingerprints, partialFingerprints, or rule + location."""
    if result.get("fingerprints"):
        return (
            "fp",
            tuple(sorted((str(k), str(v)) for k, v in result["fingerprints"].items())),
        )
    if result.get("partialFingerprints"):
        return (
            "pfp",
            tuple(
                sorted(
                    (str(k), str(v)) for k, v in result["partialFingerprints"].items()
                )
            ),
        )
    loc = (result.get("locations") or [{}])[0]
    phys = loc.get("physicalLocation") or {}
    art = phys.get("artifactLocation") or {}
    region = phys.get("region") or {}
    return (
        "loc",
        result.get("ruleId", ""),
        normalize_uri(art.get("uri")),
        region.get("startLine"),
        region.get("startColumn"),
    )


def load_sarif(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
    if "runs" not in data:
        msg = f"Missing 'runs' in SARIF: {path}"
        raise ValueError(msg)
    return data


def summarize_sarif(data: dict[str, Any]) -> dict[str, Any]:
    """Aggregate counts by level and ruleId across all runs."""
    by_level: Counter[str] = Counter()
    by_rule: Counter[str] = Counter()
    total = 0
    for run in data.get("runs") or []:
        for result in run.get("results") or []:
            total += 1
            by_level[str(result.get("level") or "warning")] += 1
            by_rule[str(result.get("ruleId") or "unknown")] += 1
    return {
        "total_results": total,
        "by_level": dict(by_level),
        "by_rule": dict(by_rule.most_common(50)),
    }


def merge_sarif_files(paths: list[Path]) -> dict[str, Any]:
    """Combine runs from multiple SARIF files; dedupe results per run bucket by fingerprint."""
    merged: dict[str, Any] = {"version": "2.1.0", "$schema": data_schema(), "runs": []}
    seen_global: set[tuple[Any, ...]] = set()

    for path in paths:
        data = load_sarif(path)
        for run in data.get("runs") or []:
            tool_name = ((run.get("tool") or {}).get("driver") or {}).get(
                "name", "unknown-tool"
            )
            new_results: list[dict[str, Any]] = []
            for result in run.get("results") or []:
                key = (tool_name, result_fingerprint(result))
                if key in seen_global:
                    continue
                seen_global.add(key)
                new_results.append(result)
            new_run = dict(run)
            new_run["results"] = new_results
            merged["runs"].append(new_run)

    return merged


def data_schema() -> str:
    return "https://json.schemastore.org/sarif-2.1.0.json"
