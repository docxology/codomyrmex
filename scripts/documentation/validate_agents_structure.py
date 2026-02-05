#!/usr/bin/env python3
"""Validate AGENTS.md structure against standards.

Ensures AGENTS.md files follow the expected structure:
- Required sections
- Proper formatting
- AI agent instructions are complete
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple


REQUIRED_SECTIONS = [
    "Purpose",
    "Key Files",
    "Dependencies",
    "Development Guidelines",
]

OPTIONAL_SECTIONS = [
    "Code Style",
    "Testing",
    "Integration Points",
    "Common Tasks",
]


class ValidationResult(NamedTuple):
    """Result of AGENTS.md validation."""
    file: str
    valid: bool
    missing_sections: list
    warnings: list
    score: int  # 0-100


def validate_agents_file(file_path: Path, repo_root: Path) -> ValidationResult:
    """Validate a single AGENTS.md file."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return ValidationResult(str(file_path), False, [], [str(e)], 0)
    
    file_str = str(file_path.relative_to(repo_root))
    missing_sections = []
    warnings = []
    score = 100
    
    # Check for required sections
    for section in REQUIRED_SECTIONS:
        # Look for heading with section name
        pattern = rf'^#+\s+{re.escape(section)}'
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            missing_sections.append(section)
            score -= 20
    
    # Check for optional sections (warn if missing, don't penalize)
    for section in OPTIONAL_SECTIONS:
        pattern = rf'^#+\s+{re.escape(section)}'
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            warnings.append(f"Consider adding '{section}' section")
    
    # Check minimum content
    if len(content) < 200:
        warnings.append("File appears too short")
        score -= 10
    
    # Check for headings
    headings = re.findall(r'^#+\s+.+$', content, re.MULTILINE)
    if len(headings) < 3:
        warnings.append("File has very few sections")
        score -= 10
    
    # Check for code blocks or file references
    has_code = '```' in content
    has_file_refs = re.search(r'`[a-zA-Z_/]+\.[a-zA-Z]+`', content)
    if not has_code and not has_file_refs:
        warnings.append("No code blocks or file references found")
    
    valid = len(missing_sections) == 0
    
    return ValidationResult(file_str, valid, missing_sections, warnings, max(0, score))


def validate_agents_structure(repo_root: Path, output_dir: Path = None, 
                             output_format: str = 'both') -> int:
    """Validate all AGENTS.md files in the repository."""
    print("🤖 Validating AGENTS.md structure...\n")
    
    if output_dir is None:
        output_dir = repo_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results: list[ValidationResult] = []
    
    # Find all AGENTS.md files
    agents_files = list(repo_root.rglob("AGENTS.md"))
    agents_files = [f for f in agents_files if ".git" not in str(f)]
    
    if not agents_files:
        print("⚠️  No AGENTS.md files found")
        return 0
    
    print(f"📄 Found {len(agents_files)} AGENTS.md files")
    
    for agents_file in agents_files:
        result = validate_agents_file(agents_file, repo_root)
        results.append(result)
    
    # Calculate stats
    valid_count = sum(1 for r in results if r.valid)
    avg_score = sum(r.score for r in results) / len(results) if results else 0
    
    # Output results
    if output_format in ('json', 'both'):
        json_path = output_dir / "agents_validation.json"
        with open(json_path, 'w') as f:
            json.dump([r._asdict() for r in results], f, indent=2)
        print(f"📄 JSON report: {json_path}")
    
    if output_format in ('markdown', 'both'):
        md_path = output_dir / "agents_validation.md"
        with open(md_path, 'w') as f:
            f.write("# AGENTS.md Validation Report\n\n")
            f.write(f"- **Valid Files**: {valid_count}/{len(results)}\n")
            f.write(f"- **Average Score**: {avg_score:.1f}/100\n\n")
            
            invalid = [r for r in results if not r.valid]
            if invalid:
                f.write("## Invalid Files\n\n")
                for r in invalid:
                    f.write(f"### `{r.file}` - {r.score}/100\n")
                    f.write("**Missing Sections:**\n")
                    for section in r.missing_sections:
                        f.write(f"- {section}\n")
                    f.write("\n")
        print(f"📄 Markdown report: {md_path}")
    
    # Summary
    print(f"\n✅ Valid: {valid_count}/{len(results)}")
    print(f"📊 Average Score: {avg_score:.1f}/100")
    
    invalid = [r for r in results if not r.valid]
    if invalid:
        print("\n❌ Invalid AGENTS.md files:")
        for r in invalid:
            print(f"   {r.file}: missing {', '.join(r.missing_sections)}")
        return 1 if '--fail-on-invalid' in sys.argv else 0
    
    print("\n✅ All AGENTS.md files are valid!")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Validate AGENTS.md structure")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=['json', 'markdown', 'both'], default='both')
    parser.add_argument("--fail-on-invalid", action="store_true")
    
    args = parser.parse_args()
    return validate_agents_structure(args.repo_root, args.output, args.format)


if __name__ == "__main__":
    sys.exit(main())
