#!/usr/bin/env python3
"""Enforce quality gates for documentation.

This script enforces thresholds for:
- Quality scores
- Broken link counts
- Placeholder counts (sum of per-file placeholder_count from analyze_content_quality.py:
  task-style TODO/FIXME/XXX and bracket tags; not prose "TODO" or example.com URLs)
- AGENTS.md validity rates
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _load_report(path: Path, label: str) -> tuple[Any | None, str | None]:
    """Load a required JSON report and return an actionable failure message."""
    if not path.exists():
        return None, f"{label} results not found: {path}"
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"{label} results could not be read: {exc}"
    if not isinstance(data, list) or not data:
        return None, f"{label} results are empty or have an invalid shape"
    return data, None


def enforce_quality_gate(
    repo_root: Path,
    output_dir: Path | None = None,
    min_quality_score: int = 70,
    max_broken_links: int = 10,
    max_placeholders: int = 100,
    min_agents_valid_rate: int = 80,
    allow_warnings: bool = False,
) -> int:
    """Enforce documentation quality gates."""
    print("🚦 Enforcing documentation quality gates...\n")

    if output_dir is None:
        output_dir = repo_root / "output"

    failures = []
    warnings = []

    # Every report is required.  A missing artifact means the corresponding
    # validator did not complete, and must not be interpreted as a pass.
    link_data, link_error = _load_report(
        output_dir / "link_validation.json", "Link validation"
    )
    if link_error:
        failures.append(link_error)
    else:
        assert isinstance(link_data, list)
        broken_count = sum(
            1
            for entry in link_data
            if isinstance(entry, dict) and entry.get("status") == "broken"
        )
        malformed = [entry for entry in link_data if not isinstance(entry, dict)]
        if malformed:
            failures.append("Link validation results contain malformed entries")
        elif broken_count > max_broken_links:
            failures.append(
                f"Broken links ({broken_count}) exceeds maximum ({max_broken_links})"
            )
        else:
            print(f"✅ Broken links: {broken_count}/{max_broken_links}")

    quality_data, quality_error = _load_report(
        output_dir / "content_quality.json", "Content quality"
    )
    if quality_error:
        failures.append(quality_error)
    else:
        assert isinstance(quality_data, list)
        if any(
            not isinstance(entry, dict)
            or not isinstance(entry.get("score"), (int, float))
            or not isinstance(entry.get("metrics"), dict)
            for entry in quality_data
        ):
            failures.append("Content quality results contain malformed entries")
        else:
            avg_score = sum(entry["score"] for entry in quality_data) / len(
                quality_data
            )
            if avg_score < min_quality_score:
                failures.append(
                    f"Average quality score ({avg_score:.1f}) below minimum ({min_quality_score})"
                )
            else:
                print(f"✅ Average quality score: {avg_score:.1f}/{min_quality_score}")

            total_placeholders = sum(
                entry["metrics"].get("placeholder_count", 0) for entry in quality_data
            )
            if not isinstance(total_placeholders, (int, float)):
                failures.append("Content quality placeholder counts are malformed")
            elif total_placeholders > max_placeholders:
                failures.append(
                    f"Placeholder count ({total_placeholders}) exceeds maximum ({max_placeholders})"
                )
            else:
                print(f"✅ Placeholders: {total_placeholders}/{max_placeholders}")

    agents_data, agents_error = _load_report(
        output_dir / "agents_validation.json", "AGENTS.md validation"
    )
    if agents_error:
        failures.append(agents_error)
    else:
        assert isinstance(agents_data, list)
        if any(
            not isinstance(entry, dict) or not isinstance(entry.get("valid"), bool)
            for entry in agents_data
        ):
            failures.append("AGENTS.md validation results contain malformed entries")
        else:
            valid_count = sum(1 for entry in agents_data if entry["valid"])
            valid_rate = (valid_count / len(agents_data)) * 100
            if valid_rate < min_agents_valid_rate:
                failures.append(
                    f"AGENTS.md valid rate ({valid_rate:.1f}%) below minimum ({min_agents_valid_rate}%)"
                )
            else:
                print(
                    f"✅ AGENTS.md valid rate: {valid_rate:.1f}%/{min_agents_valid_rate}%"
                )

    # Report warnings
    if warnings and not allow_warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"   - {w}")

    # Report failures
    if failures:
        print(f"\n❌ Quality Gate FAILED ({len(failures)} issues):")
        for f in failures:
            print(f"   - {f}")
        return 1

    print("\n✅ All quality gates passed!")
    return 0


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "documentation"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/documentation/config.yaml")

    parser = argparse.ArgumentParser(description="Enforce documentation quality gates")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-quality-score", type=int, default=70)
    parser.add_argument("--max-broken-links", type=int, default=10)
    parser.add_argument("--max-placeholders", type=int, default=100)
    parser.add_argument("--min-agents-valid-rate", type=int, default=80)
    parser.add_argument("--allow-warnings", action="store_true")

    args = parser.parse_args()
    return enforce_quality_gate(
        args.repo_root,
        args.output,
        args.min_quality_score,
        args.max_broken_links,
        args.max_placeholders,
        args.min_agents_valid_rate,
        args.allow_warnings,
    )


if __name__ == "__main__":
    sys.exit(main())
