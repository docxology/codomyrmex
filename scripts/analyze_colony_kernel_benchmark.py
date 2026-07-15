#!/usr/bin/env python3
"""Produce evidence-labeled benchmark analysis and a conservative status figure.

The script never upgrades fixture or missing results to empirical evidence. A provider
result is labeled ``provider_backed_unverified`` until the independent release verifier
has checked its receipts, registry, partitions, and metric recomputation.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from evaluations.colony_kernel.analysis import ANALYSIS_SCHEMA_VERSION, analyze_rows

ANALYSIS_SCHEMA = "benchmark-analysis-v1"


def classify_result(result: dict[str, Any] | None) -> tuple[str, str]:
    if not result:
        return "not_available", "no benchmark result is present"
    if result.get("execution_class") == "fixture_contract":
        return "fixture_contract", "fixture output is contractual evidence only"
    provider = result.get("provider")
    endpoint = provider.get("endpoint") if isinstance(provider, dict) else None
    if (
        result.get("status") == "passed"
        and result.get("execution_class") == "provider_backed"
        and isinstance(endpoint, str)
        and endpoint.startswith(("http://", "https://"))
    ):
        return (
            "provider_backed_unverified",
            "provider-backed input is present; independent release verification remains required",
        )
    return "not_available", "result is not a complete provider-backed benchmark input"


def _svg_status(label: str, detail: str, *, analysis: dict[str, Any] | None) -> str:
    safe_label = html.escape(label.replace("_", " ").upper())
    safe_detail = html.escape(detail)
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="360" viewBox="0 0 1000 360">',
        '<rect width="1000" height="360" fill="#0b1220"/>',
        '<rect x="30" y="30" width="940" height="300" rx="18" fill="#111c2e" stroke="#56b4e9" stroke-width="2"/>',
        '<text x="60" y="90" fill="#e8edf5" font-family="sans-serif" font-size="28" font-weight="bold">COLONY KERNEL BENCHMARK EVIDENCE</text>',
        f'<text x="60" y="155" fill="#f0e442" font-family="sans-serif" font-size="32" font-weight="bold">{safe_label}</text>',
        f'<text x="60" y="200" fill="#c6d3e3" font-family="sans-serif" font-size="18">{safe_detail}</text>',
    ]
    if analysis:
        denominators = analysis.get("denominators", {})
        lines.append(
            f'<text x="60" y="260" fill="#c6d3e3" font-family="sans-serif" font-size="18">Rows analyzed: {html.escape(str(denominators.get("row_denominator", 0)))} | Exact paired interval: recorded in JSON</text>'
        )
    lines.extend(
        [
            '<text x="60" y="302" fill="#8fa7bf" font-family="sans-serif" font-size="16">This figure is a provenance status card, not an effectiveness claim.</text>',
            "</svg>",
        ]
    )
    return "\n".join(lines) + "\n"


def build_analysis(result_path: Path) -> dict[str, Any]:
    result: dict[str, Any] | None = None
    if result_path.is_file():
        loaded = json.loads(result_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            result = loaded
    evidence_status, reason = classify_result(result)
    rows = result.get("rows") if result else None
    analysis = analyze_rows(rows) if isinstance(rows, list) and all(isinstance(row, dict) for row in rows) else None
    return {
        "schema_version": ANALYSIS_SCHEMA,
        "statistics_version": ANALYSIS_SCHEMA_VERSION,
        "evidence_status": evidence_status,
        "empirical_effect_claim_permitted": evidence_status == "provider_backed_unverified",
        "reason": reason,
        "source_result": str(result_path),
        "analysis": analysis,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--result",
        type=Path,
        default=Path("output/evaluations/colony_kernel/benchmark.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/data/colony_kernel_analysis.json"),
    )
    parser.add_argument(
        "--figure",
        type=Path,
        default=Path("output/figures/colony_kernel_evidence_status.svg"),
    )
    args = parser.parse_args(argv)
    payload = build_analysis(args.result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.figure.parent.mkdir(parents=True, exist_ok=True)
    args.figure.write_text(
        _svg_status(payload["evidence_status"], payload["reason"], analysis=payload["analysis"]),
        encoding="utf-8",
    )
    print(json.dumps({"output": str(args.output), "figure": str(args.figure), "evidence_status": payload["evidence_status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
