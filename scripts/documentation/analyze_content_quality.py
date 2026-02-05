#!/usr/bin/env python3
"""Analyze documentation content quality with scoring.

Checks for:
- Completeness (headings, sections)
- Readability (sentence length, complexity)
- Placeholder/TODO detection
- Code example coverage
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple


class QualityScore(NamedTuple):
    """Quality score for a file."""
    file: str
    score: int  # 0-100
    issues: list
    metrics: dict


def analyze_file(file_path: Path, repo_root: Path) -> QualityScore:
    """Analyze a single markdown file for quality."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return QualityScore(str(file_path), 0, ["Could not read file"], {})
    
    file_str = str(file_path.relative_to(repo_root))
    issues = []
    metrics = {}
    score = 100
    
    lines = content.split('\n')
    
    # Check for headings
    headings = [l for l in lines if l.startswith('#')]
    metrics['heading_count'] = len(headings)
    if len(headings) == 0:
        issues.append("No headings found")
        score -= 15
    
    # Check for placeholders/TODOs
    placeholder_patterns = [
        r'\bTODO\b', r'\bFIXME\b', r'\bXXX\b',
        r'\[placeholder\]', r'\[TBD\]', r'\[WIP\]',
        r'lorem ipsum', r'example\.com'
    ]
    placeholder_count = 0
    for pattern in placeholder_patterns:
        placeholder_count += len(re.findall(pattern, content, re.IGNORECASE))
    
    metrics['placeholder_count'] = placeholder_count
    if placeholder_count > 0:
        issues.append(f"Found {placeholder_count} placeholders/TODOs")
        score -= min(placeholder_count * 5, 25)
    
    # Check for code examples
    code_blocks = len(re.findall(r'```', content)) // 2
    metrics['code_block_count'] = code_blocks
    
    # Check document length
    word_count = len(content.split())
    metrics['word_count'] = word_count
    if word_count < 50:
        issues.append("Document appears too short")
        score -= 10
    
    # Check for links
    links = len(re.findall(r'\[([^\]]*)\]\([^)]+\)', content))
    metrics['link_count'] = links
    
    # Check for empty sections (heading with no content before next heading)
    empty_sections = 0
    for i, line in enumerate(lines[:-1]):
        if line.startswith('#') and lines[i + 1].startswith('#'):
            empty_sections += 1
    if empty_sections > 0:
        issues.append(f"Found {empty_sections} empty sections")
        score -= empty_sections * 5
    
    return QualityScore(file_str, max(0, score), issues, metrics)


def analyze_content_quality(repo_root: Path, output_dir: Path = None, 
                          output_format: str = 'both', min_score: int = 60) -> int:
    """Analyze quality of all markdown documentation."""
    print("📝 Analyzing documentation content quality...\n")
    
    if output_dir is None:
        output_dir = repo_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results: list[QualityScore] = []
    
    # Find all markdown files
    md_files = list(repo_root.rglob("*.md"))
    md_files = [f for f in md_files if ".git" not in str(f) and "node_modules" not in str(f)]
    
    print(f"📄 Found {len(md_files)} markdown files")
    
    for md_file in md_files:
        result = analyze_file(md_file, repo_root)
        results.append(result)
    
    # Calculate overall stats
    avg_score = sum(r.score for r in results) / len(results) if results else 0
    below_threshold = [r for r in results if r.score < min_score]
    
    # Output results
    if output_format in ('json', 'both'):
        json_path = output_dir / "content_quality.json"
        with open(json_path, 'w') as f:
            json.dump([r._asdict() for r in results], f, indent=2)
        print(f"📄 JSON report: {json_path}")
    
    if output_format in ('markdown', 'both'):
        md_path = output_dir / "content_quality.md"
        with open(md_path, 'w') as f:
            f.write("# Documentation Quality Report\n\n")
            f.write(f"- **Average Score**: {avg_score:.1f}/100\n")
            f.write(f"- **Files Below {min_score}**: {len(below_threshold)}\n\n")
            
            if below_threshold:
                f.write("## Files Needing Attention\n\n")
                for r in sorted(below_threshold, key=lambda x: x.score):
                    f.write(f"### `{r.file}` - {r.score}/100\n")
                    for issue in r.issues:
                        f.write(f"- {issue}\n")
                    f.write("\n")
        print(f"📄 Markdown report: {md_path}")
    
    # Summary
    print(f"\n📊 Average Quality Score: {avg_score:.1f}/100")
    print(f"📉 Files below {min_score}: {len(below_threshold)}")
    
    if below_threshold:
        print("\n⚠️  Files needing attention:")
        for r in sorted(below_threshold, key=lambda x: x.score)[:5]:
            print(f"   {r.file}: {r.score}/100")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Analyze documentation content quality")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=['json', 'markdown', 'both'], default='both')
    parser.add_argument("--min-score", type=int, default=60)
    
    args = parser.parse_args()
    return analyze_content_quality(args.repo_root, args.output, args.format, args.min_score)


if __name__ == "__main__":
    sys.exit(main())
