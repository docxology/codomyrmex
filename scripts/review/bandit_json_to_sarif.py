#!/usr/bin/env python3
"""Convert Bandit JSON report to SARIF 2.1.0 for GitHub code scanning upload."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from sarif_utils import data_schema


def _severity_to_level(sev: str | None) -> str:
    key = (sev or "").upper()
    if key == "HIGH":
        return "error"
    if key == "MEDIUM":
        return "warning"
    if key == "LOW":
        return "note"
    return "warning"


def bandit_json_to_sarif(
    data: dict[str, Any], bandit_version: str = "unknown"
) -> dict[str, Any]:
    """Map Bandit JSON (results list) to a minimal valid SARIF log."""
    sarif_results: list[dict[str, Any]] = []
    for item in data.get("results") or []:
        fn = str(item.get("filename") or "unknown")
        line = int(item.get("line_number") or 1)
        rule = str(item.get("test_id") or item.get("test_name") or "bandit")
        text = str(item.get("issue_text") or item.get("test_name") or rule)
        sarif_results.append(
            {
                "ruleId": rule,
                "level": _severity_to_level(item.get("issue_severity")),
                "message": {"text": text},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": fn},
                            "region": {"startLine": line},
                        }
                    }
                ],
            }
        )

    return {
        "version": "2.1.0",
        "$schema": data_schema(),
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Bandit",
                        "version": bandit_version,
                        "informationUri": "https://bandit.readthedocs.io/",
                    }
                },
                "results": sarif_results,
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bandit JSON → SARIF 2.1.0")
    parser.add_argument("input_json", type=Path, help="Bandit -f json report")
    parser.add_argument("output_sarif", type=Path, help="Output .sarif path")
    args = parser.parse_args()
    try:
        raw = args.input_json.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Failed to read JSON: {e}", file=sys.stderr)
        empty = {"version": "2.1.0", "$schema": data_schema(), "runs": []}
        args.output_sarif.write_text(json.dumps(empty, indent=2), encoding="utf-8")
        return 1
    if not isinstance(data, dict):
        print("Bandit JSON root must be an object", file=sys.stderr)
        return 2
    bver = "unknown"
    try:
        import bandit as bandit_mod

        bver = getattr(bandit_mod, "__version__", "unknown")
    except ImportError:
        pass
    sarif = bandit_json_to_sarif(data, bandit_version=bver)
    args.output_sarif.write_text(json.dumps(sarif, indent=2), encoding="utf-8")
    n = len(sarif["runs"][0]["results"])
    print(f"Wrote {args.output_sarif} with {n} result(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
