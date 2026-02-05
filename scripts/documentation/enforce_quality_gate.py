#!/usr/bin/env python3
"""Enforce quality gates for documentation.

This script enforces thresholds for:
- Quality scores
- Broken link counts
- Placeholder counts
- AGENTS.md validity rates
"""

import argparse
import json
import sys
from pathlib import Path


def enforce_quality_gate(
    repo_root: Path,
    output_dir: Path = None,
    min_quality_score: int = 70,
    max_broken_links: int = 10,
    max_placeholders: int = 100,
    min_agents_valid_rate: int = 80,
    allow_warnings: bool = False
) -> int:
    """Enforce documentation quality gates."""
    print("🚦 Enforcing documentation quality gates...\n")
    
    if output_dir is None:
        output_dir = repo_root / "output"
    
    failures = []
    warnings = []
    
    # Check link validation
    links_path = output_dir / "link_validation.json"
    if links_path.exists():
        with open(links_path) as f:
            link_data = json.load(f)
            broken_count = len([l for l in link_data if l['status'] == 'broken'])
            
            if broken_count > max_broken_links:
                failures.append(f"Broken links ({broken_count}) exceeds maximum ({max_broken_links})")
            else:
                print(f"✅ Broken links: {broken_count}/{max_broken_links}")
    else:
        warnings.append("Link validation results not found")
    
    # Check content quality
    quality_path = output_dir / "content_quality.json"
    if quality_path.exists():
        with open(quality_path) as f:
            quality_data = json.load(f)
            
            if quality_data:
                avg_score = sum(q['score'] for q in quality_data) / len(quality_data)
                
                if avg_score < min_quality_score:
                    failures.append(f"Average quality score ({avg_score:.1f}) below minimum ({min_quality_score})")
                else:
                    print(f"✅ Average quality score: {avg_score:.1f}/{min_quality_score}")
                
                # Check placeholders
                total_placeholders = sum(q['metrics'].get('placeholder_count', 0) for q in quality_data)
                if total_placeholders > max_placeholders:
                    failures.append(f"Placeholder count ({total_placeholders}) exceeds maximum ({max_placeholders})")
                else:
                    print(f"✅ Placeholders: {total_placeholders}/{max_placeholders}")
    else:
        warnings.append("Content quality results not found")
    
    # Check AGENTS.md validation
    agents_path = output_dir / "agents_validation.json"
    if agents_path.exists():
        with open(agents_path) as f:
            agents_data = json.load(f)
            
            if agents_data:
                valid_count = len([a for a in agents_data if a['valid']])
                valid_rate = (valid_count / len(agents_data)) * 100
                
                if valid_rate < min_agents_valid_rate:
                    failures.append(f"AGENTS.md valid rate ({valid_rate:.1f}%) below minimum ({min_agents_valid_rate}%)")
                else:
                    print(f"✅ AGENTS.md valid rate: {valid_rate:.1f}%/{min_agents_valid_rate}%")
    else:
        warnings.append("AGENTS.md validation results not found")
    
    # Report warnings
    if warnings:
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
        args.repo_root, args.output,
        args.min_quality_score, args.max_broken_links,
        args.max_placeholders, args.min_agents_valid_rate,
        args.allow_warnings
    )


if __name__ == "__main__":
    sys.exit(main())
